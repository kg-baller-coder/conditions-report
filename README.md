# Conditions Report

A command-line tool that pulls weather, snowpack, and avalanche danger for
Colorado ski and backcountry spots into one morning report.

## Why I built this

Every morning before heading up to the mountains, I was checking three
separate sites -- Mountain Forecast for weather, Windy for wind/snow, and
CAIC for avalanche danger -- to decide where to go and whether it was safe.
This project replaces that routine with one script and one summary, and
doubles as a hands-on project for learning to work with public REST APIs,
config-driven design, and error handling in Python.

## What it does

For each location in `config/locations.yaml`, it pulls:
- **Weather** -- 3-day forecast (temp, wind, precipitation/snow) from the
  [National Weather Service API](https://www.weather.gov/documentation/services-web-api)
- **Snowpack** -- current snow depth, snow water equivalent, and 24-72 hour
  change from the nearest [NRCS SNOTEL](https://www.nrcs.usda.gov/resources/data-and-reports/snow-telemetry-snotel) station
- **Avalanche danger** -- current danger rating for the relevant CAIC zone,
  via the [avalanche.org Public API](https://github.com/NationalAvalancheCenter/Avalanche.org-Public-API-Docs)

...and prints it all as one clean terminal report, plus saves and opens a
styled `report.html` version. All three data sources are free, public, and
require no API key.

## How to run it

```bash
git clone https://github.com/kg-baller-coder/conditions-report.git
cd conditions-report
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

To track your own spots, edit `config/locations.yaml` -- no code changes
needed. Each entry needs a lat/lon and the nearest NRCS SNOTEL station ID
(find one at [wcc.sc.egov.usda.gov/nwcc](https://wcc.sc.egov.usda.gov/nwcc/)).

## Using this outside Colorado

The weather (`weather.py`) and snowpack (`snowpack.py`) modules work
anywhere in the US -- the NWS and SNOTEL networks both cover the whole
country. The avalanche module (`avalanche.py`) is CAIC-specific, but the
same avalanche.org API covers every US avalanche center, so pointing it at
a different `center_id` (e.g. `"UAC"` for Utah) is a small, contained
change rather than a rewrite.

## Contributing

This started as a personal/learning project, so it's intentionally small
and simple rather than fully generalized -- but pull requests, issues, and
forks are welcome. `CLAUDE.md` has the design notes and reasoning behind
the current structure if you want context before changing something.

## Tech

Python, `requests`, `PyYAML`. No database or framework -- kept intentionally
simple. See [CLAUDE.md](CLAUDE.md) for design notes and current build status.

## Roadmap

- Save daily data to SQLite to track trends over a season
- Charts of snowpack over time
- Scheduled daily run that emails/texts the report

## License

[MIT](LICENSE) -- use it, fork it, change it.
