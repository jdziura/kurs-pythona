import os
import json
from unittest.mock import patch

from bus_project.data_collection.collect_data import (
    collect_stops_data,
    collect_schedule_data,
    collect_routes_data,
    process_measurements,
)


def test_collect_stops_data(tmp_path):
    with patch('bus_project.data_collection.collect_data.get_stops_data') as mock_get_stops_data:
        with patch('bus_project.data_collection.collect_data.get_lines_data') as mock_get_lines_data:
            stops_response = {"result": [
                {'values': [
                    {'key': 'zespol', 'value': '200'},
                    {'key': 'slupek', 'value': '1'},
                    {"key": 'nazwa_zespolu', "value": "Przystanek"},
                    {'key': 'szer_geo', 'value': '123.456'},
                    {'key': 'dlug_geo', 'value': '456.789'}
                ]}
            ]}
            lines_response = {'result': [
                {'values': [{'value': '123'}]},
                {'values': [{'value': '456'}]}
            ]}
            mock_get_stops_data.return_value = stops_response
            mock_get_lines_data.return_value = lines_response

            test_data_dir = tmp_path / 'test_data'
            os.makedirs(test_data_dir, exist_ok=True)

            collect_stops_data(test_data_dir)

            json_file_path = test_data_dir / 'stops.json'

            expected_response = [{
                "busstop_id": "200",
                "busstop_nr": "1",
                "name": "Przystanek",
                "lon": "456.789",
                "lat": "123.456",
                "lines": ['123', '456']
            }]

            assert json_file_path.exists()
            with open(json_file_path) as json_file:
                json_data = json.load(json_file)

            print(json_data, expected_response)

            assert json_data == expected_response


def test_collect_schedule_data(tmp_path):
    with patch('bus_project.data_collection.collect_data.get_schedule_data') as mock_get_schedule_data:
        stops_data = [{
            "busstop_id": "200",
            "busstop_nr": "1",
            "name": "Przystanek",
            "lon": "456.789",
            "lat": "123.456",
            "lines": ['123', '456']
        }]

        schedules_response = {'result': [
            {'values': [
                {'key': 'czas', 'value': '08:00'},
                {'key': 'kierunek', 'value': 'Direction 1'},
                {'key': 'trasa', 'value': 'Route 1'},
                {'key': 'brygada', 'value': '1'}
            ]},
            {'values': [
                {'key': 'czas', 'value': '08:15'},
                {'key': 'kierunek', 'value': 'Direction 2'},
                {'key': 'trasa', 'value': 'Route 2'},
                {'key': 'brygada', 'value': '2'}
            ]}
        ]}

        expected_response = [{
            "busstop_id": "200",
            "busstop_nr": "1",
            "line": '123',
            "schedule": [
                {'time': '08:00', 'direction': 'Direction 1',
                    'route': 'Route 1', 'brigade': '1'},
                {'time': '08:15', 'direction': 'Direction 2',
                    'route': 'Route 2', 'brigade': '2'}
            ]
        }, {
            "busstop_id": "200",
            "busstop_nr": "1",
            "line": '456',
            "schedule": [
                {'time': '08:00', 'direction': 'Direction 1',
                    'route': 'Route 1', 'brigade': '1'},
                {'time': '08:15', 'direction': 'Direction 2',
                    'route': 'Route 2', 'brigade': '2'}
            ]
        }]

        mock_get_schedule_data.return_value = schedules_response

        test_data_dir = tmp_path / 'test_data'
        os.makedirs(test_data_dir, exist_ok=True)

        with open(test_data_dir / 'stops.json', 'w') as f:
            json.dump(stops_data, f)

        collect_schedule_data(test_data_dir)

        json_file_path = test_data_dir / 'schedules.json'

        assert json_file_path.exists()
        with open(json_file_path) as json_file:
            json_data = json.load(json_file)

        assert json_data == expected_response


def test_collect_routes_data(tmp_path):
    routes_data = {
        '123': {
            'A': {
                '1': {'nr_zespolu': '200', 'nr_przystanku': '1'},
                '2': {'nr_zespolu': '201', 'nr_przystanku': '2'}
            },
            'B': {
                '1': {'nr_zespolu': '202', 'nr_przystanku': '1'},
                '2': {'nr_zespolu': '203', 'nr_przystanku': '2'}
            }
        },
        '456': {
            'C': {
                '1': {'nr_zespolu': '204', 'nr_przystanku': '1'},
                '2': {'nr_zespolu': '205', 'nr_przystanku': '2'}
            }
        }
    }

    expected_response = {
        '123': {
            'A': [
                {'busstop_id': '200', 'busstop_nr': '1'},
                {'busstop_id': '201', 'busstop_nr': '2'}
            ],
            'B': [
                {'busstop_id': '202', 'busstop_nr': '1'},
                {'busstop_id': '203', 'busstop_nr': '2'}
            ]
        },
        '456': {
            'C': [
                {'busstop_id': '204', 'busstop_nr': '1'},
                {'busstop_id': '205', 'busstop_nr': '2'}
            ]
        }
    }

    with patch('bus_project.data_collection.collect_data.get_routes_data') as mock_get_routes_data:
        mock_get_routes_data.return_value = {'result': routes_data}

        test_data_dir = tmp_path / 'test_data'
        os.makedirs(test_data_dir, exist_ok=True)

        collect_routes_data(test_data_dir)

        json_file_path = test_data_dir / 'routes.json'

        assert json_file_path.exists()
        with open(json_file_path) as json_file:
            json_data = json.load(json_file)

        assert json_data == expected_response


def test_process_measurements(tmp_path):
    test_data_dir = tmp_path / 'test_data'
    os.makedirs(test_data_dir, exist_ok=True)

    data1 = {
        'result': [
            {'VehicleNumber': '123', 'Lines': [
                'A'], 'Brigade': '1', 'Time': '2024-02-21 12:00:00', 'Lat': '52.2323', 'Lon': '21.0456'},
            {'VehicleNumber': '123', 'Lines': [
                'A'], 'Brigade': '1', 'Time': '2024-02-21 12:05:00', 'Lat': '52.2324', 'Lon': '21.0457'}
        ]
    }
    data2 = {
        'result': [
            {'VehicleNumber': '456', 'Lines': [
                'B'], 'Brigade': '2', 'Time': '2024-02-21 12:02:00', 'Lat': '52.2345', 'Lon': '21.0567'}
        ]
    }

    with open(test_data_dir / 'data1.json', 'w') as f:
        json.dump(data1, f)
    with open(test_data_dir / 'data2.json', 'w') as f:
        json.dump(data2, f)

    process_measurements(test_data_dir)

    assert (test_data_dir / 'processed.json').exists()

    with open(test_data_dir / 'processed.json', 'r') as f:
        processed_data = json.load(f)

    expected_processed_data = {
        '123': {
            'Lines': ['A'],
            'Brigade': '1',
            'Measurements': [
                {'Time': '2024-02-21 12:00:00', 'Lat': '52.2323', 'Lon': '21.0456'},
                {'Time': '2024-02-21 12:05:00', 'Lat': '52.2324', 'Lon': '21.0457'}
            ]
        },
        '456': {
            'Lines': ['B'],
            'Brigade': '2',
            'Measurements': [
                {'Time': '2024-02-21 12:02:00', 'Lat': '52.2345', 'Lon': '21.0567'}
            ]
        }
    }

    assert processed_data == expected_processed_data
