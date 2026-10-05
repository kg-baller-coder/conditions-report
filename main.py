"""
Entry point: run `python main.py` to print the conditions report for every
location in config/locations.yaml.
"""

import yaml

from conditions_report import weather, snowpack, report


def load_locations(path="config/locations.yaml"):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config["locations"]


def main():
    locations = load_locations()

    for loc in locations:
        weather_periods = weather.get_forecast(loc["lat"], loc["lon"])
        snow = snowpack.get_snowpack(loc["snotel_station"])
        report.print_location_report(loc["name"], weather_periods, snow)


if __name__ == "__main__":
    main()
