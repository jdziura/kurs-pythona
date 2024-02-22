from datetime import datetime
import json

from bus_project.data_analysis.utils import haversine
from bus_project.data_analysis.analyze_data import (
    nearest_stop_from_list,
    nearest_stop,
    approx_time_at_stop,
    get_punctualities,
    analyze_punctuality
)


def test_nearest_stop_from_list():
    point1 = (52.2323, 21.0456)
    point2 = (52.2333, 21.0556)

    stops = [
        {'busstop_id': '1', 'busstop_nr': '101'},
        {'busstop_id': '2', 'busstop_nr': '102'},
        {'busstop_id': '3', 'busstop_nr': '103'}
    ]
    stops_coords = {
        ('1', '101'): (52.2324, 21.0457),
        ('2', '102'): (52.2330, 21.0540),
        ('3', '103'): (52.2340, 21.0560)
    }

    closest_stop, closest_distance = nearest_stop_from_list(
        point1, point2, stops, stops_coords)

    expected_closest_stop = {'busstop_id': '1', 'busstop_nr': '101'}
    expected_closest_distance = haversine(point1[0], point1[1], stops_coords[(
        '1', '101')][0], stops_coords[('1', '101')][1])

    assert closest_stop == expected_closest_stop
    assert closest_distance == expected_closest_distance


def test_nearest_stop():
    point1 = (52.2323, 21.0456)
    point2 = (52.2333, 21.0556)

    line = 'A'

    stops_coords = {
        ('1', '101'): (52.2324, 21.0457),
        ('2', '102'): (52.2330, 21.0540),
        ('3', '103'): (52.2340, 21.0560)
    }

    routes_data = {
        'A': {
            'route1': [{'busstop_id': '1', 'busstop_nr': '101'}, {'busstop_id': '2', 'busstop_nr': '102'}],
            'route2': [{'busstop_id': '3', 'busstop_nr': '103'}]
        }
    }

    closest_stop, _ = nearest_stop(
        point1, point2, line, stops_coords, routes_data)

    expected_closest_stop = {'busstop_id': '1', 'busstop_nr': '101'}

    assert closest_stop == expected_closest_stop


def test_approx_time_at_stop():
    time1 = datetime(2024, 2, 21, 12, 0, 0)
    time2 = datetime(2024, 2, 21, 12, 10, 0)

    point1 = (52.2323, 21.0456)
    point2 = (52.2333, 21.0556)

    point_stop = (52.2324, 21.0457)

    approx_time = approx_time_at_stop(time1, time2, point1, point2, point_stop)

    expected_time = time1 + (time2 - time1) * (
        haversine(point1[0], point1[1], point_stop[0], point_stop[1]) /
        (haversine(point1[0], point1[1], point_stop[0], point_stop[1]) +
            haversine(point2[0], point2[1], point_stop[0], point_stop[1]))
    )

    assert approx_time == expected_time


def test_get_punctualities():
    bus = {
        "Measurements": [
            {"Time": "2024-02-21 12:00:00", "Lat": 52.2323, "Lon": 21.0456},
            {"Time": "2024-02-21 12:10:00", "Lat": 52.2333, "Lon": 21.0556}
        ],
        "Lines": "A"
    }

    routes_data = {
        "A": {
            "route1": [
                {'busstop_id': '1', 'busstop_nr': '101'},
                {'busstop_id': '2', 'busstop_nr': '102'}
            ]
        }
    }

    stops_coords = {
        ('1', '101'): (52.2323, 21.0456),
        ('2', '102'): (52.2333, 21.0556)
    }

    punctualities = get_punctualities(bus, routes_data, stops_coords)

    assert len(punctualities) == 1


def test_analyze_punctuality(tmp_path):
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()

    live_data = {
        "bus1": {"Lines": "123", "Measurements": [
            {"Time": "2024-02-21 12:00:00", "Lat": 52.2323, "Lon": 21.0456},
            {"Time": "2024-02-21 12:10:00", "Lat": 52.2333, "Lon": 21.0556}
        ]},
        "bus2": {"Lines": "456", "Measurements": [
            {"Time": "2024-02-21 13:00:00", "Lat": 52.2323, "Lon": 21.0456},
            {"Time": "2024-02-21 13:10:00", "Lat": 52.2333, "Lon": 21.0556}
        ]}
    }
    routes_data = {
        '123': {
            'A': [
                {'busstop_id': '1', 'busstop_nr': '1'},
            ],
            'B': [
                {'busstop_id': '1', 'busstop_nr': '1'},
            ]
        },
        '456': {
            'C': [
                {'busstop_id': '1', 'busstop_nr': '1'},
            ]
        }}
    stops_data = [{"busstop_id": "1", "busstop_nr": "1",
                   "lon": "21.0506", "lat": "52.2328",
                   "lines": ["123", "456"]}]
    schedules_data = [
        {"busstop_id": "1", "busstop_nr": "1", "line": "123", "schedule": [
            {"time": "2024-02-21 12:00:00"},
            {"time": "2024-02-21 12:10:00"}
        ]},
        {"busstop_id": "1", "busstop_nr": "1", "line": "456", "schedule": [
            {"time": "2024-02-21 13:00:00"},
            {"time": "2024-02-21 13:10:00"}
        ]}
    ]

    with open(data_dir / "live_data.json", "w") as f:
        json.dump(live_data, f)
    with open(data_dir / "routes.json", "w") as f:
        json.dump(routes_data, f)
    with open(data_dir / "stops.json", "w") as f:
        json.dump(stops_data, f)
    with open(data_dir / "schedules.json", "w") as f:
        json.dump(schedules_data, f)

    analyze_punctuality(data_dir / "live_data.json", data_dir)
