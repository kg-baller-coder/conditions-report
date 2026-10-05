"""
Builds a styled HTML version of the report and saves it to disk.

This is plain HTML with CSS written right into the page (no separate
stylesheet, no JavaScript, no web fonts) -- it works completely offline
once generated, which matters if you're checking this from spotty
mountain wifi. Each run overwrites report.html with fresh data.
"""

import os
import webbrowser
from datetime import datetime

# report.html lives at the project root, one level up from this file's
# folder (conditions_report/).
OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "report.html"
)

# Gray CAIC itself uses for "no rating" -- used as a fallback if a danger
# dict somehow doesn't have a color.
DEFAULT_DANGER_COLOR = "#888888"


def _weather_html(periods):
    if periods is None:
        return '<p class="unavailable">Weather unavailable.</p>'

    cards = []
    for p in periods:
        precip = (p.get("probabilityOfPrecipitation") or {}).get("value")
        precip_html = f'<span class="precip">{precip}% precip</span>' if precip else ""
        cards.append(f"""
        <div class="period">
          <div class="period-head">
            <span class="period-name">{p['name']}</span>
            <span class="period-temp">{p['temperature']}&deg;{p['temperatureUnit']}</span>
          </div>
          <div class="period-wind">wind {p['windSpeed']} {p['windDirection']} {precip_html}</div>
          <div class="period-text">{p['detailedForecast']}</div>
        </div>""")
    return "\n".join(cards)


def _change_html(value, label):
    """One small badge like "▲ +2 in depth", colored by direction."""
    if value is None:
        return f'<span class="change flat">n/a {label}</span>'
    if value > 0:
        return f'<span class="change up">&#9650; +{value} {label}</span>'
    if value < 0:
        return f'<span class="change down">&#9660; {value} {label}</span>'
    return f'<span class="change flat">&#8211; {value} {label}</span>'


def _snowpack_html(snow):
    if snow is None:
        return '<p class="unavailable">Snowpack unavailable.</p>'

    return f"""
    <div class="stat-row">
      <div class="stat">
        <div class="stat-value">{snow['depth_in']}&Prime;</div>
        <div class="stat-label">depth</div>
      </div>
      <div class="stat">
        <div class="stat-value">{snow['swe_in']}&Prime;</div>
        <div class="stat-label">snow water equiv.</div>
      </div>
    </div>
    <div class="snow-changes">
      <div>24h &nbsp; {_change_html(snow['depth_change_24h'], 'depth')} &nbsp; {_change_html(snow['swe_change_24h'], 'SWE')}</div>
      <div>72h &nbsp; {_change_html(snow['depth_change_72h'], 'depth')} &nbsp; {_change_html(snow['swe_change_72h'], 'SWE')}</div>
    </div>
    <div class="as-of">as of {snow['date']}</div>
    """


def _avalanche_html(avy):
    if avy is None:
        return '<p class="unavailable">Avalanche info unavailable.</p>'

    color = avy.get("color", DEFAULT_DANGER_COLOR)
    if avy["danger_level"] == -1:
        label = "SEASON NOT STARTED"
    else:
        label = f"{avy['danger'].upper()} &middot; level {avy['danger_level']}/5"

    return f"""
    <div class="danger-badge" style="background:{color};">{label}</div>
    <p class="zone-name">{avy['zone_name']}</p>
    <p class="advice">{avy['travel_advice']}</p>
    <a class="forecast-link" href="{avy['link']}" target="_blank" rel="noopener">
      Full CAIC forecast &rarr;
    </a>
    """


def _location_card_html(result):
    return f"""
    <section class="card">
      <h2>{result['name']}</h2>
      <div class="section">
        <h3>Weather <span class="sub">next 3 days</span></h3>
        {_weather_html(result['weather'])}
      </div>
      <div class="section">
        <h3>Snowpack</h3>
        {_snowpack_html(result['snowpack'])}
      </div>
      <div class="section">
        <h3>Avalanche Danger</h3>
        {_avalanche_html(result['avalanche'])}
      </div>
    </section>
    """


# Using .format() with a template this size gets messy because CSS also
# uses curly braces, so the {generated}/{cards} placeholders below are
# filled in with simple .replace() calls instead in build_html().
PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Colorado Conditions Report</title>
<style>
  :root {
    --bg: #f4f6f8;
    --card-bg: #ffffff;
    --text: #1b1f23;
    --muted: #6b7280;
    --border: #e3e6ea;
    --accent: #2b6cb0;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #15181c;
      --card-bg: #1f2328;
      --text: #e9ecef;
      --muted: #9aa4af;
      --border: #30353b;
      --accent: #6fa8dc;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 24px 16px 48px;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  header { text-align: center; margin-bottom: 28px; }
  header h1 { margin: 0 0 4px; font-size: 1.5rem; }
  header p { margin: 0; color: var(--muted); font-size: 0.9rem; }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    max-width: 1100px;
    margin: 0 auto;
  }
  .card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
  }
  .card h2 { margin: 0 0 12px; font-size: 1.2rem; }
  .section { margin-top: 18px; }
  .section h3 {
    margin: 0 0 8px;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
  }
  .section h3 .sub { text-transform: none; letter-spacing: 0; font-weight: normal; }

  .period { padding: 8px 0; border-top: 1px solid var(--border); }
  .period:first-child { border-top: none; }
  .period-head { display: flex; justify-content: space-between; font-weight: 600; }
  .period-wind { color: var(--muted); font-size: 0.85rem; margin: 2px 0; }
  .period-text { font-size: 0.85rem; margin-top: 2px; }
  .precip { color: var(--accent); }

  .stat-row { display: flex; gap: 24px; }
  .stat-value { font-size: 1.6rem; font-weight: 700; }
  .stat-label { color: var(--muted); font-size: 0.75rem; text-transform: uppercase; }
  .snow-changes { margin-top: 10px; font-size: 0.85rem; color: var(--muted); }
  .snow-changes div { margin-top: 2px; }
  .change.up { color: #2b6cb0; }
  .change.down { color: #c05621; }
  .change.flat { color: var(--muted); }
  .as-of { margin-top: 8px; font-size: 0.75rem; color: var(--muted); }

  .danger-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    color: #fff;
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 0.02em;
  }
  .zone-name { margin: 8px 0 4px; font-weight: 600; font-size: 0.9rem; }
  .advice { margin: 0 0 8px; font-size: 0.85rem; color: var(--muted); }
  .forecast-link { font-size: 0.85rem; color: var(--accent); text-decoration: none; }
  .forecast-link:hover { text-decoration: underline; }

  .unavailable { color: var(--muted); font-style: italic; font-size: 0.85rem; }

  footer {
    max-width: 1100px;
    margin: 32px auto 0;
    padding-top: 16px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.8rem;
    text-align: center;
  }
</style>
</head>
<body>
  <header>
    <h1>Colorado Conditions Report</h1>
    <p>generated __GENERATED__</p>
  </header>
  <div class="grid">
    __CARDS__
  </div>
  <footer>
    For planning only. Always check the official CAIC forecast before heading into avalanche terrain.
  </footer>
</body>
</html>
"""


def build_html(results):
    now = datetime.now().strftime("%A, %B %d, %Y &middot; %I:%M %p")
    cards = "\n".join(_location_card_html(r) for r in results)
    return PAGE_TEMPLATE.replace("__GENERATED__", now).replace("__CARDS__", cards)


def write_report(results, auto_open=True):
    """Build the HTML, save it to report.html, and (by default) open it
    in your default browser. Returns the file path."""
    html = build_html(results)
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)
    if auto_open:
        webbrowser.open(f"file://{OUTPUT_PATH}")
    return OUTPUT_PATH
