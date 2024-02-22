import requests
from bus_project.data_collection.utils import make_safe_request

import pytest


@pytest.fixture
def mock_requests_get(monkeypatch):
    def mock_get(url, params, timeout):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if url == 'http://example.com/success':
            return MockResponse({"result": ["some", "data"]}, 200)
        elif url == 'http://example.com/failure1':
            return MockResponse({"result": "an error occured"}, 200)
        elif url == 'http://example.com/failure2':
            return MockResponse({"result": "failure"}, 400)
        else:
            raise ValueError("Invalid URL")

    monkeypatch.setattr(requests, 'get', mock_get)


def test_make_safe_request_success(mock_requests_get):
    url = 'http://example.com/success'
    params = {'param1': 'value1'}
    response = make_safe_request(url, params)
    assert response == {"result": ["some", "data"]}


def test_make_safe_request_failure1(mock_requests_get):
    url = 'http://example.com/failure'
    params = {'param1': 'value1'}
    response = make_safe_request(url, params)
    assert response is None


def test_make_safe_request_failure2(mock_requests_get):
    url = 'http://example.com/failure2'
    params = {'param1': 'value1'}
    response = make_safe_request(url, params)
    assert response is None


def test_make_safe_request_exception(mock_requests_get, monkeypatch):
    def mock_exception(*args, **kwargs):
        raise Exception("Mocked exception")

    monkeypatch.setattr(requests, 'get', mock_exception)
    url = 'http://example.com/exception'
    params = {'param1': 'value1'}
    response = make_safe_request(url, params)
    assert response is None
