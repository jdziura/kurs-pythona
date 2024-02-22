"""
This module is used to collect data of buses in Warsaw. It provides
functionality to download basic information about buses and stops,
as well as live data of buses positions.
"""

import argparse
import os

from bus_project.data_collection.collect_data import collect_basic_data
from bus_project.data_collection.collect_data import collect_live_data


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Analyze data of bus in Warsaw.')

    parser.add_argument('--base', action='store_true',
                        help='Download base data of buses and stops')
    parser.add_argument('--live', action='store_true',
                        help='Download live data of buses positions')

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.base:
        collect_basic_data()

    if args.live:
        required_files = ["stops.json", "routes.json", "schedules.json"]

        for file in required_files:
            file_path = os.path.join("data", file)
            if not os.path.exists(file_path):
                print("Some basic data is missing")
                print("Please download it first by using --base option.")
                print(f"Missing file: {file}")
                return

        collect_live_data(60)


if __name__ == "__main__":
    main()
