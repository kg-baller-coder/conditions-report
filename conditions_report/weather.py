"""
Weather forecasts from the National Weather Service (NWS) API.

Docs: https://www.weather.gov/documentation/services-web-api
No API key needed -- it's a free public API run by the US government.

How the NWS API works (two steps):
  1. You give it a lat/lon via the /points/{lat},{lon} endpoint.
     It doesn't return a forecast directly -- it returns metadata, including
     a URL for the forecast specific to that location's "grid".
  2. You fetch that forecast URL to get the actual day-by-day forecast.

We do it in two steps here because that's genuinely how the API is designed --
it's split this way so NWS can serve forecasts from many different regional
offices behind the scenes.
"""

import requests

# NWS asks every caller to send a User-Agent identifying the app, so they
# can contact someone if a script is misbehaving. It doesn't have to be
# fancy, just identifying.
HEADERS = {"User-Agent": "conditions-report (personal project, github.com/kg-baller-coder)"}

BASE_URL = "https://api.weather.gov"


def get_forecast(lat, lon, periods=6):
    """
    Return a list of forecast periods for the given coordinates.

    NWS splits each day into a "day" and "night" period, so periods=6 gets
    roughly 3 days of coverage. Each period is a dict with fields like
    name, temperature, windSpeed, windDirection, and detailedForecast
    (which includes precipitation chances and snow amounts in its text).

    Returns None if the lookup fails for any reason, so the caller can
    skip this source and keep going rather than crash the whole report.
    """
    try:
        # Step 1: turn lat/lon into the right forecast grid endpoint.
        points_url = f"{BASE_URL}/points/{lat},{lon}"
        points_resp = requests.get(points_url, headers=HEADERS, timeout=10)
        points_resp.raise_for_status()  # raises an exception on a 4xx/5xx response
        forecast_url = points_resp.json()["properties"]["forecast"]

        # Step 2: fetch the actual forecast from that URL.
        forecast_resp = requests.get(forecast_url, headers=HEADERS, timeout=10)
        forecast_resp.raise_for_status()
        all_periods = forecast_resp.json()["properties"]["periods"]

        return all_periods[:periods]

    except requests.RequestException as e:
        # Covers connection errors, timeouts, and bad status codes.
        print(f"  [weather] could not fetch forecast: {e}")
        return None
    except (KeyError, IndexError) as e:
        # Covers the response coming back without the fields we expected.
        print(f"  [weather] unexpected response shape: {e}")
        return None


if __name__ == "__main__":
    # Quick manual test: run `python conditions_report/weather.py` to check
    # this module works on its own, before main.py ties everything together.
    periods = get_forecast(39.4817, -106.1319)  # Copper Mountain
    if periods:
        for p in periods:
            print(f"{p['name']}: {p['temperature']}°{p['temperatureUnit']}, "
                  f"wind {p['windSpeed']} {p['windDirection']}")
            print(f"  {p['detailedForecast']}\n")
