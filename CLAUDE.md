# Conditions Report

## Goal
A command-line tool that pulls together weather, snowpack, and avalanche danger
for a handful of Colorado ski/backcountry spots into one printed report --
replacing a morning routine of checking Mountain Forecast, Windy, and CAIC
separately.

This is a learning project and a portfolio piece for an MIS/Data Science
student. Code should stay simple, well-commented, and explain new concepts
as they're introduced -- not just "working."

## Tech stack
- Python 3
- `requests` for HTTP calls to public APIs (no API keys needed for any of them)
- `PyYAML` for reading the location config
- Data sources:
  - Weather: [National Weather Service API](https://www.weather.gov/documentation/services-web-api) (api.weather.gov)
  - Snowpack: [NRCS SNOTEL / AWDB REST API](https://wcc.sc.egov.usda.gov/awdbRestApi/) (wcc.sc.egov.usda.gov)
  - Avalanche danger: [avalanche.org Public API](https://github.com/NationalAvalancheCenter/Avalanche.org-Public-API-Docs) (api.avalanche.org), the official API run by the National Avalanche Center that includes CAIC's zones. CAIC itself has no public API -- this is the sanctioned alternative; we deliberately do not scrape avalanche.state.co.us.

## How to run it
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Locations live in `config/locations.yaml` -- add a spot by adding a block there,
no code changes needed.

## Project layout
```
conditions-report/
├── config/locations.yaml     # spots: name, lat/lon, nearest SNOTEL station
├── conditions_report/
│   ├── weather.py            # NWS API calls
│   ├── snowpack.py           # SNOTEL API calls
│   ├── avalanche.py          # avalanche.org API calls
│   └── report.py             # combines everything, formats + prints
└── main.py                   # entry point
```

## Design notes
- Each data source module can fail independently -- `report.py` wraps each
  call in a try/except so one API being down doesn't take out the whole report.
- The avalanche module determines a location's CAIC zone by checking its
  lat/lon against CAIC's zone polygons (fetched from the avalanche.org API),
  rather than storing a zone ID in config. Zone boundaries don't line up
  neatly with place names (e.g. Loveland Pass sits right on a zone boundary),
  so computing it is more correct than guessing.
- The avalanche.org API gives a zone's danger rating, color, and short travel
  advice, plus a link to CAIC's full written discussion -- not the full
  avalanche-problem text. That's enough for a summary line; we link out for
  the rest rather than scraping it.

## Later / not built yet
- Save each day's data to a SQLite database to track trends over the season
- Charts of snowpack over time
- Run automatically every morning, email or text the report

## Current status
_(updated at the end of each session)_

**2026-10-04:** Project scaffolded. Repo created at
`~/Projects/conditions-report`, pushed to GitHub (private,
`kg-baller-coder/conditions-report`). Confirmed all three data sources are
public/free/no-key. `config/locations.yaml` set up with Copper Mountain,
Loveland Pass, and Vail Pass (coordinates + nearest SNOTEL station looked up
for each).

`weather.py` (NWS) and `snowpack.py` (SNOTEL) are both built, tested
standalone, and wired into `main.py`/`report.py`. `python main.py` prints a
working report for all three locations. Decided to keep output terminal-only
for now (matches the "script I run each morning" use case); a prettier
format or HTML/web version is a possible later step, not needed now.
Snowpack numbers are all 0 right now since it's pre-season (early October) --
logic is confirmed correct, just no snow to report yet.

**2026-10-04 (cont'd):** `avalanche.py` built -- fetches CAIC zones from the
avalanche.org map-layer API and uses a hand-written point-in-polygon check
(ray casting, no extra dependency) to find which zone a location falls in.
Tested standalone against all three locations, then wired into
`report.py`/`main.py`. All three data sources (weather, snowpack, avalanche)
now run end to end for all three locations with `python main.py`.

Note: CAIC's forecast season hasn't started yet (it's early October), so the
API currently returns one combined "off-season" zone with "no rating" for
the whole state rather than individual named zones. The code handles this
correctly already (prints "forecast season hasn't started yet"), but the
multi-zone, real-danger-rating path (e.g. "Vail & Summit County: considerable")
hasn't been seen with live data yet -- worth a sanity check once the season
opens, usually mid-November.

MVP is functionally complete: all three sources work, each fails gracefully
on its own, config-driven locations, clean terminal report.

**2026-10-04 (cont'd):** Polish pass done -- `report.py` now prints a
header with a generated timestamp, consistent section dividers, wrapped
text so nothing runs off the terminal width, ▲/▼ arrows for snowpack
change, ANSI color coding for avalanche danger level (1-5), and a safety
disclaimer footer. `v1` / MVP is complete: `python main.py` prints a full,
readable report for all three locations from a fresh clone.

**2026-10-04 (cont'd):** Added `html_report.py` -- generates a styled,
self-contained `report.html` (no external fonts/JS, works offline) each
run, using the same data the terminal report uses. Card-per-location
layout, avalanche danger badges colored using CAIC's own `color` value
from the API (not a hardcoded guess), light/dark mode via
`prefers-color-scheme`. `main.py` now fetches all data once into a list of
dicts, then feeds both the terminal printer and the HTML builder from it.
Opens automatically in the default browser via `webbrowser.open()`;
`report.html` is gitignored since it's regenerated every run.

Shell alias `conditions` (in `~/.zshrc`) runs the whole thing from any
terminal: cd's into the project, activates the venv, runs `main.py`.

**2026-10-04 (cont'd):** Re-themed `report.html` to dark grey / light blue
(dropped the earlier light/dark auto-switching -- this is now a fixed
theme) and restyled headings to an overline-label + bold-heading +
short-dash pattern (inspired by a design Konnor shared), applied to both
the hero header and each location card. Added a statewide avalanche
synopsis: `avalanche.get_statewide_summary()` looks at ALL of CAIC's
zones (not just the ones your 3 spots fall in) and summarizes danger
levels across the state; shown in a small banner under the hero heading.
Currently reports "season hasn't started" since it's pre-season --
worth a look once CAIC's season opens to confirm the real breakdown text
reads well with multiple zones/ratings.

Next: nothing required. Candidates for a future session: SQLite history,
snowpack charts, scheduled daily run (see "Later" above) -- or just revisit
once the season opens to confirm the avalanche sections look right with
real multi-zone, rated forecasts.
