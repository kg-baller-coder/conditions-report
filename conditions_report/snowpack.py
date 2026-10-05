"""
Current snowpack from NRCS SNOTEL stations, via the AWDB (Air & Water
Database) REST API.

Docs: https://wcc.sc.egov.usda.gov/awdbRestApi/
Free, public, no API key -- it's a USDA government service.

Each SNOTEL station is identified by a "station triplet" like "415:CO:SNTL"
(station number : state : network). We ask for two "elements":
  - SNWD = snow depth (inches)
  - WTEQ = snow water equivalent (inches) -- how much water the snowpack
           would produce if melted all at once. This is the number
           avalanche/hydrology folks actually care about, since a foot of
           fluffy powder and a foot of wet spring snow hold very
           different amounts of water.

We request several days of history (not just today) so we can work out how
much has changed over the last 24 and 72 hours -- the station doesn't hand
you a "change" number directly, so we calculate it ourselves.
"""

from datetime import date, timedelta

import requests

BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data"

# How many days of history to pull. We need at least 3 days back for the
# 72-hour comparison, plus a couple extra in case the most recent day or
# two hasn't posted yet.
LOOKBACK_DAYS = 6


def _fetch_element_series(station_triplet, element_code):
    """Return {date_string: value} for one element, oldest to newest."""
    end = date.today()
    begin = end - timedelta(days=LOOKBACK_DAYS)

    params = {
        "stationTriplets": station_triplet,
        "elements": element_code,
        "duration": "DAILY",
        "beginDate": begin.isoformat(),
        "endDate": end.isoformat(),
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    body = resp.json()

    if not body or not body[0].get("data"):
        return {}

    values = body[0]["data"][0]["values"]
    return {v["date"]: v["value"] for v in values}


def get_snowpack(station_triplet):
    """
    Return current snow depth / SWE and their 24h and 72h change for a
    SNOTEL station.

    Returns a dict like:
        {
            "date": "2026-10-03",         # most recent date with data
            "depth_in": 14,
            "swe_in": 2.1,
            "depth_change_24h": 1,        # None if not enough history
            "depth_change_72h": 3,
            "swe_change_24h": 0.2,
            "swe_change_72h": 0.5,
        }
    Returns None if the station can't be reached at all.
    """
    try:
        depth_series = _fetch_element_series(station_triplet, "SNWD")
        swe_series = _fetch_element_series(station_triplet, "WTEQ")
    except requests.RequestException as e:
        print(f"  [snowpack] could not fetch {station_triplet}: {e}")
        return None

    if not depth_series or not swe_series:
        print(f"  [snowpack] no data returned for {station_triplet}")
        return None

    # The most recent date either series has data for. Sorting as strings
    # works fine here since the dates are in YYYY-MM-DD format.
    latest_date = max(depth_series)
    latest = date.fromisoformat(latest_date)

    def change(series, days):
        """Difference between today's value and the value `days` ago, or
        None if that older reading isn't in the series."""
        past_date = (latest - timedelta(days=days)).isoformat()
        if latest_date not in series or past_date not in series:
            return None
        return round(series[latest_date] - series[past_date], 2)

    return {
        "date": latest_date,
        "depth_in": depth_series[latest_date],
        "swe_in": swe_series[latest_date],
        "depth_change_24h": change(depth_series, 1),
        "depth_change_72h": change(depth_series, 3),
        "swe_change_24h": change(swe_series, 1),
        "swe_change_72h": change(swe_series, 3),
    }


if __name__ == "__main__":
    # Quick manual test: python conditions_report/snowpack.py
    data = get_snowpack("415:CO:SNTL")  # Copper Mountain station
    print(data)
