"""
Builds and prints the final report by combining each data source's output.

Keeping this separate from main.py means: main.py just loads config and
calls things, and this file just worries about how the output looks.
"""

import textwrap
from datetime import datetime

LINE_WIDTH = 64
WRAP_WIDTH = LINE_WIDTH - 4  # leaves room for indenting wrapped text

# ANSI escape codes for colored terminal text. "\033[32m" switches following
# text to green, "\033[0m" resets back to normal -- every terminal that
# isn't ancient understands these. We use them to make avalanche danger
# (1 low -> 5 extreme) readable at a glance, the way CAIC's own site does.
DANGER_COLORS = {
    1: "\033[32m",  # green
    2: "\033[93m",  # yellow
    3: "\033[33m",  # orange/dark yellow
    4: "\033[31m",  # red
    5: "\033[41m",  # red background -- extreme is rare and should stand out
}
RESET = "\033[0m"


def _wrap(text, indent="    "):
    """Wrap long text to LINE_WIDTH so paragraphs don't run off the edge
    of a normal terminal window."""
    return textwrap.fill(text, width=WRAP_WIDTH, initial_indent=indent,
                          subsequent_indent=indent)


def _fmt_change(value, unit):
    """Format a +/- change value with an arrow, or a placeholder if the
    data wasn't available to compute it."""
    if value is None:
        return "n/a"
    if value > 0:
        return f"▲ +{value} {unit}"  # ▲
    if value < 0:
        return f"▼ {value} {unit}"  # ▼
    return f"– {value} {unit}"  # –


def print_report_header():
    now = datetime.now().strftime("%A, %B %d, %Y  %I:%M %p")
    print("=" * LINE_WIDTH)
    print("COLORADO CONDITIONS REPORT".center(LINE_WIDTH))
    print(f"generated {now}".center(LINE_WIDTH))
    print("=" * LINE_WIDTH)


def print_report_footer():
    print()
    print("-" * LINE_WIDTH)
    print(_wrap(
        "For planning only. Always check the official CAIC forecast "
        "(linked above) before heading into avalanche terrain.",
        indent=""
    ))


def print_weather_section(periods):
    """Print a weather forecast section. `periods` is the list returned by
    weather.get_forecast(), or None if that source failed."""
    print("  WEATHER (next 3 days)")
    if periods is None:
        print("    [unavailable]")
        return

    for p in periods:
        temp = f"{p['temperature']}°{p['temperatureUnit']}"
        wind = f"wind {p['windSpeed']} {p['windDirection']}"
        print(f"    {p['name']:<14} {temp:>6}   {wind}")
        print(_wrap(p["detailedForecast"], indent="      "))


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

    level = avalanche["danger_level"]
    if level == -1:
        print(f"    {avalanche['zone_name']}: forecast season hasn't started yet")
    else:
        color = DANGER_COLORS.get(level, "")
        print(f"    {avalanche['zone_name']}: "
              f"{color}{avalanche['danger'].upper()} (level {level}/5){RESET}")
    print(_wrap(avalanche["travel_advice"]))
    print(f"    full forecast: {avalanche['link']}")


def print_location_report(name, weather_periods, snowpack, avalanche):
    """Print the full report for one location."""
    print()
    print("-" * LINE_WIDTH)
    print(f"  {name.upper()}")
    print("-" * LINE_WIDTH)
    print_weather_section(weather_periods)
    print()
    print_snowpack_section(snowpack)
    print()
    print_avalanche_section(avalanche)
