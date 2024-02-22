"""
This module is used to analyze data of buses in Warsaw. It provides
functionality to analyze punctuality and speed of buses via command line
interface.
"""

import argparse
import os
import line_profiler

from bus_project.data_analysis.utils import haversine
from bus_project.data_analysis.analyze_data import (
    analyze_punctuality,
    analyze_speed,
    analyze_depots,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Analyze data of buses in Warsaw.')

    parser.add_argument('action', nargs='?', default=None, choices=['show'],
                        help='Action to perform, show or analyze. ' +
                        '(default: analyze)')
    parser.add_argument('--punctuality', action='store_true',
                        help='Analyze punctuality of buses')
    parser.add_argument('--speed', action='store_true',
                        help='Analyze speed of buses')
    parser.add_argument('--depots', action='store_true',
                        help='Analyze buses in depots')
    parser.add_argument('--data_dir', type=str,
                        help='Path to the data directory')
    parser.add_argument('--speed_limit', type=int,
                        help='Speed limit for speed analysis')
    parser.add_argument('--profile', action='store_true',
                        help='Profile code execution with line_profiler')

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.profile:
        profiler = line_profiler.LineProfiler()
        profiler.add_function(haversine)
        profiler.add_function(analyze_depots)
        profiler.add_function(analyze_punctuality)
        profiler.add_function(analyze_speed)

        if args.action == 'show' or args.data_dir is None:
            print("List of available live data timestamps:")

            for file in sorted(os.listdir("data/live/")):
                print(file)
        else:
            filepath = f"data/live/{args.data_dir}/processed.json"
            profiler.runctx("analyze_speed(filepath, 50)",
                            globals(), locals())
            profiler.runctx("analyze_depots(filepath)",
                            globals(), locals())
            profiler.runctx("analyze_punctuality(filepath)",
                            globals(), locals())

        profiler.print_stats()
        return

    if args.action == 'show' or args.data_dir is None:
        print("List of available live data timestamps:")

        for file in sorted(os.listdir("data/live/")):
            print(file)

        return

    if args.data_dir not in os.listdir("data/live/"):
        print(f"Data timestamp {args.data_dir} does not exist.")
        print("List of available live data timestamps:")

        for file in sorted(os.listdir("data/live/")):
            print(file)

        return

    filepath = f"data/live/{args.data_dir}/processed.json"

    if args.speed:
        speed_limit = args.speed_limit if args.speed_limit else 50
        analyze_speed(filepath, speed_limit)

    if args.depots:
        analyze_depots(filepath)

    if args.punctuality:
        analyze_punctuality(filepath)


if __name__ == "__main__":
    main()
