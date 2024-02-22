""" Module for collecting data from the Warsaw public transport API. """
import os
import json
import datetime
import time
import concurrent.futures
from tqdm import tqdm

from .utils import (
    get_stops_data,
    get_live_data,
    get_lines_data,
    get_schedule_data,
    get_routes_data,
)

DATA_DIR = 'data'

# pylint: disable=unspecified-encoding


def collect_stops_data(output_dir: str = DATA_DIR) -> None:
    """
    Collects the basic data of all bus stops in Warsaw from the Warsaw public
    transport API and saves it to a JSON file.
    """
    filepath = os.path.join(output_dir, 'stops.json')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    data = get_stops_data()
    processed_data = []
    all_lines = set()

    def process_item(item):
        item = item['values']
        item_dict = {pair['key']: pair['value'] for pair in item}

        current_dict = {
            "busstop_id": item_dict['zespol'],
            "busstop_nr": item_dict['slupek'],
            "name": item_dict['nazwa_zespolu'],
            "lon": item_dict['dlug_geo'],
            "lat": item_dict['szer_geo'],
        }

        lines_data = get_lines_data(item_dict['zespol'], item_dict['slupek'])
        i = 0
        while lines_data is None:
            i += 1
            if i % 3 == 0:
                time.sleep(1)
            lines_data = get_lines_data(
                item_dict['zespol'], item_dict['slupek'])

        lines_data = lines_data['result']
        stop_lines = [line['values'][0]['value'] for line in lines_data]
        all_lines.update(stop_lines)

        current_dict['lines'] = stop_lines
        processed_data.append(current_dict)

    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        futures = [executor.submit(process_item, item)
                   for item in data['result']]

        for future in tqdm(concurrent.futures.as_completed(futures),
                           total=len(futures),
                           desc="Downloading stops data"):
            future.result()

    with open(filepath, 'w') as f:
        json.dump(processed_data, f)

    print(f"Saved bus stops data to {filepath}")


def collect_schedule_data(output_dir: str = DATA_DIR) -> None:
    """
    Collects the schedule data of all bus stops in from the Warsaw public
    transport API and saves it to a JSON file.
    """
    with open(f'{output_dir}/stops.json') as f:
        stops_data = json.load(f)

    filepath = os.path.join(output_dir, 'schedules.json')
    schedule_data = []

    def process_line(item, line):
        schedule = get_schedule_data(
            item['busstop_id'], item['busstop_nr'], line)

        i = 0
        while schedule is None:
            i += 1
            if i % 3 == 0:
                time.sleep(1)

            schedule = get_schedule_data(
                item['busstop_id'], item['busstop_nr'], line)

        schedule = schedule['result']

        schedule = [{item['key']: item['value']
                     for item in sched['values']} for sched in schedule]
        schedule = [{
            'time': sched['czas'],
            'direction': sched['kierunek'],
            'route': sched['trasa'],
            'brigade': sched['brygada'],
        } for sched in schedule]

        schedule_data.append({
            'busstop_id': item['busstop_id'],
            'busstop_nr': item['busstop_nr'],
            'line': line,
            'schedule': schedule
        })

    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        futures = [executor.submit(process_line, item, line)
                   for item in stops_data for line in item['lines']]

        for future in tqdm(concurrent.futures.as_completed(futures),
                           total=len(futures),
                           desc="Downloading schedules"):
            future.result()

    with open(filepath, 'w') as f:
        json.dump(schedule_data, f)

    print(f"Saved schedule data to {filepath}")


def process_measurements(data_dir: str = DATA_DIR) -> None:
    """
    Processes the measurements of live data of buses in Warsaw, accumulated
    and stored in JSON files in the specified directory, and saves the
    processed data to a single JSON file.

    Args:
        data_dir (str): The directory containing the JSON files of
            the live data.
    """
    processed_data = {}

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)

        with open(filepath, 'r') as f:
            data = json.load(f)

        assert 'result' in data

        if not isinstance(data['result'], list):
            continue

        for item in data['result']:
            vehicle_number = item['VehicleNumber']

            if vehicle_number not in processed_data:
                processed_data[vehicle_number] = {}
                processed_data[vehicle_number]['Lines'] = item['Lines']
                processed_data[vehicle_number]['Brigade'] = item['Brigade']
                processed_data[vehicle_number]['Measurements'] = []

            processed_data[vehicle_number]['Measurements'].append({
                "Time": item['Time'],
                "Lat": item['Lat'],
                "Lon": item['Lon']
            })

    for vehicle_number, data in processed_data.items():
        data['Measurements'] = sorted(
            data['Measurements'], key=lambda x: x['Time'])

    with open(os.path.join(data_dir, 'processed.json'), 'w') as f:
        json.dump(processed_data, f)


def collect_live_data(minutes: int = 60, output_dir: str = DATA_DIR) -> None:
    """
    Collects the live data of buses in Warsaw for the specified number of
    minutes and saves it to a directory in the data folder.

    Args:
        minutes (int): The number of minutes to collect the live data for.
    """
    current_time = datetime.datetime.now()
    data_dir = os.path.join(
        output_dir, 'live', current_time.strftime('%Y-%m-%d_%H:%M'))

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for i in range(minutes):
        data = get_live_data()
        repeats = 0

        while data is None and repeats < 60:
            time.sleep(1)
            repeats += 1
            data = get_live_data()

        if data is None:
            continue

        current_time = datetime.datetime.now()
        filename = f"{current_time.strftime('%Y-%m-%d_%H:%M')}.json"
        filepath = os.path.join(data_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(data, f)

        print(f"Saved live data to {filepath}")

        if i < minutes - 1:
            time.sleep(60 - repeats)

    process_measurements(data_dir)


def collect_routes_data(output_dir: str = DATA_DIR) -> None:
    """
    Collects the routes data of all bus lines in Warsaw from the Warsaw public
    transport API and saves it to a JSON file.
    """
    filepath = os.path.join(output_dir, 'routes.json')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    data = get_routes_data()
    while data is None:
        time.sleep(1)
        data = get_routes_data()

    data = data['result']

    processed_data = {}

    for line in data.keys():
        processed_data[line] = {}
        for route in data[line].keys():
            processed_data[line][route] = [{}] * len(data[line][route])
            for key, val in data[line][route].items():
                assert 0 <= int(key) - 1 < len(data[line][route])
                processed_data[line][route][int(key) - 1] = {
                    "busstop_id": val['nr_zespolu'],
                    "busstop_nr": val['nr_przystanku'],
                }

    with open(filepath, 'w') as f:
        json.dump(processed_data, f)


def collect_basic_data() -> None:
    """
    Collects all the basic data of all bus stops, routes, and schedules in
    from the Warsaw public transport API and saves it to JSON files.
    """
    collect_stops_data()
    collect_routes_data()
    collect_schedule_data()
