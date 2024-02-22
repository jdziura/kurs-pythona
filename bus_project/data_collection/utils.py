"""
This module provides utility functions for making requests to the Warsaw
public transport API.
"""

from typing import Dict, Optional
import os
import requests
from dotenv import load_dotenv

from .api_constants import (
    LIVE_DATA_ID, LIVE_DATA_URL,
    STOPS_URL, STOPS_ID,
    LINES_URL, LINES_ID, SCHEDULE_ID,
    ROUTES_URL
)


load_dotenv()


def make_safe_request(url, params) -> Optional[Dict]:
    """
    Makes a safe HTTP GET request to the specified URL with the given
    parameters. Detects failures in API calls to Warsaw public transport
    API and returns None in such cases.

    Args:
        url (str): The URL to send the request to.
        params (dict): The parameters to include in the request.

    Returns:
        dict or None: The JSON response from the request, or None if the
        request was unsuccessful.
    """
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None

        if isinstance(response.json()['result'], str):
            return None

    except Exception:
        return None

    return response.json()


def get_stops_data() -> Optional[Dict]:
    """
    Gets the basic data of all bus stops in Warsaw from the Warsaw public
    transport API.

    Returns:
        dict or None: The JSON response from the request, or None if the
        request was unsuccessful.
    """
    url = STOPS_URL
    params = {
        "id": STOPS_ID,
        "apikey": os.environ.get("API_KEY")
    }

    return make_safe_request(url, params)


def get_live_data() -> Optional[Dict]:
    """
    Gets the live data of buses in Warsaw at current moment
    from the Warsaw public transport API.

    Returns:
        dict or None: The JSON response from the request, or None if the
        request was unsuccessful.
    """
    url = LIVE_DATA_URL
    params = {
        "resource_id": LIVE_DATA_ID,
        "apikey": os.environ.get("API_KEY"),
        "type": 1
    }

    return make_safe_request(url, params)


def get_lines_data(busstop_id: str, busstop_nr: str) -> Optional[Dict]:
    """
    Gets the lines that stop at the specified bus stop
    from the Warsaw public transport API.

    Args:
        busstop_id (str): The ID of the bus stop.
        busstop_nr (str): The number of the bus stop.

    Returns:
        dict or None: The JSON response from the request, or None if the
        request was unsuccessful.
    """
    url = LINES_URL
    params = {
        "id": LINES_ID,
        "apikey": os.environ.get("API_KEY"),
        "busstopId": busstop_id,
        "busstopNr": busstop_nr
    }

    return make_safe_request(url, params)


def get_schedule_data(
    busstop_id: str, busstop_nr: str, line: str
) -> Optional[Dict]:
    """
    Gets the schedule of all the routes of the specified line
    at the specified bus stop from the Warsaw public transport API.

    Args:
        busstop_id (str): The ID of the bus stop.
        busstop_nr (str): The number of the bus stop.
        line (str): The line number.

    Returns:
        dict or None: The JSON response from the request, or None if the
        request was unsuccessful.
    """
    url = LINES_URL
    params = {
        "id": SCHEDULE_ID,
        "apikey": os.environ.get("API_KEY"),
        "busstopId": busstop_id,
        "busstopNr": busstop_nr,
        "line": line
    }

    return make_safe_request(url, params)


def get_routes_data() -> Optional[Dict]:
    """
    Gets the data of all bus routes in Warsaw from the Warsaw public
    transport API.

    Returns:
        dict or None: The JSON response from the request, or None if the
        request was unsuccessful.
    """
    url = ROUTES_URL
    params = {
        "apikey": os.environ.get("API_KEY")
    }

    return make_safe_request(url, params)
