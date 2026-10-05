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


def _fmt_change(value, unit):
    """Format a +/- change value, or a placeholder if it's unavailable."""
    if value is None:
        return "n/a"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value} {unit}"


def print_snowpack_section(snowpack):
    """Print a snowpack section. `snowpack` is the dict returned by
    snowpack.get_snowpack(), or None if that source failed."""
    print("  SNOWPACK")
    if snowpack is None:
        print("    [unavailable]")
        return

    print(f"    as of {snowpack['date']}: "
          f"depth {snowpack['depth_in']} in, SWE {snowpack['swe_in']} in")
    print(f"    24h change: depth {_fmt_change(snowpack['depth_change_24h'], 'in')}, "
          f"SWE {_fmt_change(snowpack['swe_change_24h'], 'in')}")
    print(f"    72h change: depth {_fmt_change(snowpack['depth_change_72h'], 'in')}, "
          f"SWE {_fmt_change(snowpack['swe_change_72h'], 'in')}")


def print_avalanche_section(avalanche):
    """Print an avalanche danger section. `avalanche` is the dict returned
    by avalanche.get_avalanche_danger(), or None if that source failed."""
    print("  AVALANCHE DANGER")
    if avalanche is None:
        print("    [unavailable]")
        return

    if avalanche["danger_level"] == -1:
        print(f"    {avalanche['zone_name']}: forecast season hasn't started yet")
    else:
        print(f"    {avalanche['zone_name']}: {avalanche['danger']} "
              f"(level {avalanche['danger_level']}/5)")
    print(f"    {avalanche['travel_advice']}")
    print(f"    full forecast: {avalanche['link']}")


def print_location_report(name, weather_periods, snowpack, avalanche):
    """Print the full report for one location."""
    print(f"\n=== {name} ===")
    print_weather_section(weather_periods)
    print_snowpack_section(snowpack)
    print_avalanche_section(avalanche)
