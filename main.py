"""
Entry point: run `python main.py` to print the conditions report for every
location in config/locations.yaml, and save/open a prettier HTML version.
"""

import yaml

from conditions_report import weather, snowpack, avalanche, report, html_report


def load_locations(path="config/locations.yaml"):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config["locations"]


def main():
    locations = load_locations()

    # Fetch everything first and keep it in one list of dicts -- that way
    # both the terminal printout and the HTML page are built from the same
    # data, instead of fetching it twice.
    results = []
    for loc in locations:
        weather_periods = weather.get_forecast(loc["lat"], loc["lon"])
        snow = snowpack.get_snowpack(loc["snotel_station"])
        avy = avalanche.get_avalanche_danger(loc["lat"], loc["lon"])
        results.append({
            "name": loc["name"],
            "weather": weather_periods,
            "snowpack": snow,
            "avalanche": avy,
        })

    report.print_report_header()
    for r in results:
        report.print_location_report(r["name"], r["weather"], r["snowpack"], r["avalanche"])
    report.print_report_footer()

    html_path = html_report.write_report(results)
    print(f"\nHTML report saved and opened: {html_path}")


if __name__ == "__main__":
    main()
