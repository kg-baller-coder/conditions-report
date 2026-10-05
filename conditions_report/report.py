"""
Builds and prints the final report by combining each data source's output.

Keeping this separate from main.py means: main.py just loads config and
calls things, and this file just worries about how the output looks. As we
add snowpack and avalanche data, their sections get added here.
"""


def print_weather_section(periods):
    """Print a weather forecast section. `periods` is the list returned by
    weather.get_forecast(), or None if that source failed."""
    print("  WEATHER (next 3 days)")
    if periods is None:
        print("    [unavailable]")
        return

    for p in periods:
        print(f"    {p['name']}: {p['temperature']}°{p['temperatureUnit']}, "
              f"wind {p['windSpeed']} {p['windDirection']}")
        print(f"      {p['detailedForecast']}")


def print_location_report(name, weather_periods):
    """Print the full report for one location."""
    print(f"\n=== {name} ===")
    print_weather_section(weather_periods)
