""" Module for analyzing data. """
import json
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import numpy as np
import pandas as pd
from tqdm import tqdm
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt

from .utils import haversine


def nearest_stop_from_list(
        point1: Tuple[float, float],
        point2: Tuple[float, float],
        stops: List[dict],
        stops_coords: dict
) -> Tuple[dict, float]:
    """
    Find the nearest stop from a list of stops to a line segment
    defined by two points.

    Args:
        point1 (tuple): The first point of the line segment.
        point2 (tuple): The second point of the line segment.
        stops (list): A list of stops.
        stops_coords (dict): A dictionary mapping stop IDs to their
            coordinates.

    Returns:
        tuple: A tuple containing the closest stop and the distance
            from the stop to the line segment.
    """
    closest_stop = None
    closest_distance = 0

    for stop in stops:
        if (stop['busstop_id'], stop['busstop_nr']) not in stops_coords:
            continue

        stop_lon, stop_lat = stops_coords[
            (stop['busstop_id'], stop['busstop_nr'])]

        distance = min(
            haversine(point1[0], point1[1], stop_lon, stop_lat),
            haversine(point2[0], point2[1], stop_lon, stop_lat),
        )

        if closest_stop is None or distance < closest_distance:
            closest_stop = stop
            closest_distance = distance

    return closest_stop, closest_distance


def nearest_stop(
    point1: Tuple[float, float],
    point2: Tuple[float, float],
    line: str,
    stops_coords: Dict[Tuple[str, str], Tuple[float, float]],
    routes_data: Dict[str, Dict[str, List[dict]]]
) -> Tuple[dict, float]:
    """
    Find the nearest stop (lying on specified bus line) to a
    segment defined by two points.

    Args:
        point1 (tuple): The first point of the line segment.
        point2 (tuple): The second point of the line segment.
        line (str): The line number.
        stops_coords (dict): A dictionary mapping stop IDs to their
            coordinates.
        routes_data (dict): A dictionary containing the routes data.

    Returns:
        tuple: A tuple containing the closest stop and the distance
            from the stop to the line segment.
    """
    closest_stop = None
    closest_distance = 0

    for route in routes_data[line].keys():
        stops = routes_data[line][route]

        current_closest, current_distance = nearest_stop_from_list(
            point1, point2, stops, stops_coords)

        if closest_stop is None or current_distance < closest_distance:
            closest_stop = current_closest
            closest_distance = current_distance

    return closest_stop, closest_distance


def approx_time_at_stop(
    time1: datetime,
    time2: datetime,
    point1: Tuple[float, float],
    point2: Tuple[float, float],
    point_stop: Tuple[float, float]
) -> datetime:
    """
    Approximate the time at which a bus would be at a stop
    knowing the measurements of the bus at two different times,
    and assuming that the bus stops at the specified stop.

    Args:
        time1 (datetime): The first time.
        time2 (datetime): The second time.
        point1 (tuple): The first point.
        point2 (tuple): The second point.
        point_stop (tuple): The stop point.

    Returns:
        datetime: The approximate time at which the bus would be at the stop.
    """
    return time1 + (time2 - time1) * (
        haversine(point1[0], point1[1], point_stop[0], point_stop[1]) /
        (haversine(point1[0], point1[1], point_stop[0], point_stop[1]) +
            haversine(point2[0], point2[1], point_stop[0], point_stop[1]))
    )


def get_time_distance(time1: datetime, time2: datetime) -> int:
    """
    Get the time difference in seconds between two times, ignoring the date.

    Args:
        time1 (datetime): The first time.
        time2 (datetime): The second time.

    Returns:
        int: The time difference in seconds.
    """
    t1 = time1.time()
    t2 = time2.time()

    return (t2.hour - t1.hour) * 3600 \
        + (t2.minute - t1.minute) * 60 \
        + (t2.second - t1.second)


def get_punctualities(
        bus: dict,
        routes_data: dict,
        stops_coords: dict
) -> List[Tuple[datetime, dict, float]]:
    """
    Get measured approximate timestamps at which a bus would be at
    stops on its route, and the distance from the bus to the stops.

    Args:
        bus (dict): The bus data.
        routes_data (dict): The routes data.
        stops_coords (dict): A dictionary mapping stop IDs to their
            coordinates.

    Returns:
        list: A list of tuples containing the approximate timestamps
            at which the bus would be at stops on its route, and the
            distance from the bus to the stops.
    """
    measurements = bus['Measurements']
    line = bus["Lines"]
    punctualities = []

    for i in range(1, len(measurements)):
        time1, lat1, lon1 = measurements[i-1].values()
        time2, lat2, lon2 = measurements[i].values()

        try:
            time1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
            time2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
        except Exception:
            continue

        point1 = (lon1, lat1)
        point2 = (lon2, lat2)

        closest_stop, closest_distance = nearest_stop(
            point1, point2, line, stops_coords, routes_data)

        stop_lon, stop_lat = stops_coords[
            closest_stop['busstop_id'], closest_stop['busstop_nr']]

        stop_point = (stop_lon, stop_lat)

        time_at_closest = approx_time_at_stop(
            time1, time2, point1, point2, stop_point)

        punctualities.append(
            (time_at_closest, closest_stop, closest_distance))

    return punctualities


def get_times_at_stops(
        punctualities: List[Tuple[datetime, dict, float]]
) -> List[Tuple[datetime, dict]]:
    """
    Get the final best approximate timestamps at which the bus would be
    at stops on its route.

    Args:
        punctualities (list): A list of tuples containing the measured
            approximations at which the bus would be at stops on its route,
            and the distance from the bus to the stops.

    Returns:
        list: A list of tuples containing the final best approximate.
    """
    times_at_stops = {}
    for time, stop, dist in punctualities:
        key = (stop['busstop_id'], stop['busstop_nr'])
        if key not in times_at_stops:
            times_at_stops[key] = (time, dist)
        elif times_at_stops[key][1] > dist:
            times_at_stops[key] = (time, dist)

    times_at_stops = [(val[0], stop)
                      for stop, val in times_at_stops.items()]
    times_at_stops = sorted(times_at_stops)

    return times_at_stops


def get_list_delays(
        bus: dict,
        schedules: dict,
        times_at_stops: List[Tuple[datetime, dict]]
) -> List[float]:
    """
    Get the list of all delays of a bus from known approximate arrival times.

    Args:
        bus (dict): The bus data.
        schedules (dict): The schedules data.
        times_at_stops (list): A list of tuples containing approximate
            arrival times at stops on the route.

    Returns:
        list: A list of all delays of the bus in minutes.
    """
    line = bus["Lines"]
    delays = []

    for time, stop in times_at_stops:
        schedule = schedules[(stop[0], stop[1], line)]
        relevant_schedules = []
        for sched in schedule:
            relevant_schedules.append(sched['time'])

        differences = []

        for sched in relevant_schedules:
            try:
                sched = datetime.strptime(sched, '%H:%M:%S')
            except Exception:
                continue

            time_difference_seconds = get_time_distance(
                time, sched)

            if time_difference_seconds > -120:
                differences.append(max(0, time_difference_seconds))

        if len(differences) > 0:
            delays.append(min(differences))

    return delays


def get_median_delay(
        bus: dict,
        routes_data: dict,
        stops_coords: dict,
        schedules: dict
) -> Optional[float]:
    """
    Get the median delay of a bus from known measurements.

    Args:
        bus (dict): The bus data.
        routes_data (dict): The routes data.
        stops_coords (dict): The stops coordinates data.
        schedules (dict): The schedules data.

    Returns:
        float: The median delay of the bus in minutes or None if
            cannot be calculated from the data or result is abnormal.
    """
    line = bus["Lines"]

    if line not in routes_data:
        return None

    punctualities = get_punctualities(bus, routes_data, stops_coords)
    times_at_stops = get_times_at_stops(punctualities)
    delays = get_list_delays(bus, schedules, times_at_stops)

    if len(delays) == 0:
        return None

    final_delay = np.median(delays)

    if final_delay < 3600:
        return final_delay / 60

    return None

# pylint: disable=unspecified-encoding


def analyze_punctuality(live_data_dir: str, data_dir: str = 'data') -> None:
    """
    Analyze the punctuality of buses.

    Args:
        data_dir (str): The path to the data directory.
    """
    with open(live_data_dir) as f:
        live_data = json.load(f)
    with open(f'{data_dir}/routes.json') as f:
        routes_data = json.load(f)
    with open(f'{data_dir}/stops.json') as f:
        stops_data = json.load(f)
    with open(f'{data_dir}/schedules.json') as f:
        schedules_data = json.load(f)

    stops_coordinates = {
        (stop['busstop_id'], stop['busstop_nr']):
        (float(stop['lon']), float(stop['lat']))
        for stop in stops_data
    }

    schedules = {
        (schedule['busstop_id'], schedule['busstop_nr'], schedule['line']):
        schedule["schedule"] for schedule in schedules_data
    }

    all_delays = []
    results_data = []

    for bus_id, bus in tqdm(live_data.items(), total=len(live_data),
                            desc="Analyzing punctuality"):
        delay = get_median_delay(
            bus, routes_data, stops_coordinates, schedules)
        if delay is not None:
            all_delays.append(delay)
            results_data.append((bus_id, bus["Lines"], delay))

    data_df = pd.DataFrame(results_data, columns=['Bus ID', 'Line', 'Delay'])

    if len(data_df) < 10:
        return

    top_delayed = data_df.groupby('Line')['Delay'].mean().nlargest(10)

    print("Delay statistics:\n", data_df['Delay'].describe())
    print("Top 10 lines with the highest average delay:\n", top_delayed)

    all_delays = np.array(sorted(all_delays))

    avg_delay = all_delays.mean()
    median_delay = all_delays[len(all_delays) // 2]

    avg_delay = round(avg_delay, 2)
    median_delay = round(median_delay, 2)

    plt.hist(all_delays, bins=50)
    plt.xlabel('Delay [minutes]')
    plt.ylabel('Number of buses with delay')

    plt.axvline(avg_delay, color='r', linestyle='dashed', linewidth=1,
                label=f'Average Delay: {avg_delay} min')
    plt.axvline(median_delay, color='g', linestyle='dashed', linewidth=1,
                label=f'Median Delay: {median_delay} min')

    plt.legend()

    plt.savefig('punctuality.png')

    print("Detailed plot saved to punctuality.png")


def analyze_speed(data_dir: str, speed_limit: int) -> None:
    """
    Analyze the speed of buses.

    Args:
        data_dir (str): The path to the data directory.
        speed_limit (int): The target maximum speed.
    """

    with open(data_dir) as f:
        data = json.load(f)

    speed_records = {}
    exceeding_speed_locations = []

    exceeding_speed_bus_ids = set()

    for bus_id, bus in tqdm(data.items(),
                            total=len(data),
                            desc="Analyzing speed"):
        measurements = bus['Measurements']
        speed_records[bus_id] = []

        for i in range(1, len(measurements)):
            time1, lat1, lon1 = measurements[i-1].values()
            time2, lat2, lon2 = measurements[i].values()

            try:
                time1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
                time2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
            except Exception:
                continue

            time_diff = (time2 - time1).seconds / 3600

            if time_diff == 0:
                continue

            distance = haversine(lon1, lat1, lon2, lat2)
            speed = distance / time_diff
            speed_records[bus_id].append(speed)

            if speed > speed_limit:
                exceeding_speed_locations.append(
                    ((lat1 + lat2) / 2, (lon1 + lon2) / 2))
                exceeding_speed_locations.append((lat1, lon1))
                exceeding_speed_locations.append((lat2, lon2))

                exceeding_speed_bus_ids.add(bus_id)

    map_center = [52.2297, 21.0122]  # Center of Warsaw
    m = folium.Map(location=map_center, zoom_start=12)
    HeatMap(exceeding_speed_locations).add_to(m)
    m.save('heatmap.html')

    print("Number of buses exceeding speed limit:",
          len(exceeding_speed_bus_ids), "out of", len(speed_records),
          f"({len(exceeding_speed_bus_ids)/len(speed_records)*100:.2f}%)")
    print("Detailed heatmap saved to heatmap.html")


def analyze_depots(data_dir: str) -> None:
    """
    Analyze bus staying in depots.

    Args:
        data_dir (str): The path to the data directory.
    """
    with open(data_dir) as f:
        live_data = json.load(f)

    in_depots = []

    for _, bus in tqdm(live_data.items(), total=len(live_data),
                       desc="Analyzing depots"):
        measurements = bus['Measurements']

        if len(measurements) < 5:
            continue

        time1, lat1, lon1 = measurements[0].values()
        time2, lat2, lon2 = measurements[-1].values()

        try:
            time1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
            time2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
        except Exception:
            continue

        distance = haversine(lon1, lat1, lon2, lat2)
        time_diff = (time2 - time1).seconds / 3600

        if time_diff == 0:
            continue

        speed = distance / time_diff

        if speed < 0.1 and time_diff > 0.5:
            in_depots.append((lat1, lon1))

    map_center = [52.2297, 21.0122]  # Center of Warsaw
    m = folium.Map(location=map_center, zoom_start=12)
    HeatMap(in_depots).add_to(m)
    m.save('heatmap_depots.html')

    print("Number of buses staying in depots:",
          len(in_depots), "out of", len(live_data),
          f"({len(in_depots)/len(live_data)*100:.2f}%)")
    print("Detailed heatmap saved to heatmap_depots.html")
