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

Next: avalanche module (CAIC danger via avalanche.org API), including the
point-in-polygon zone lookup described above.
