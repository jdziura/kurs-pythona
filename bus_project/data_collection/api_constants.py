"""This module contains constants used by the API requests."""

API_BASE_URL = "https://api.um.warszawa.pl/api/action"

LIVE_DATA_URL = f"{API_BASE_URL}/busestrams_get"
LIVE_DATA_ID = "f2e5503e-927d-4ad3-9500-4ab9e55deb59"

STOPS_URL = f"{API_BASE_URL}/dbstore_get"
STOPS_ID = "1c08a38c-ae09-46d2-8926-4f9d25cb0630"

LINES_URL = f"{API_BASE_URL}/dbtimetable_get"
LINES_ID = "88cd555f-6f31-43ca-9de4-66c479ad5942"
SCHEDULE_ID = "e923fa0e-d96c-43f9-ae6e-60518c9f3238"

ROUTES_URL = f"{API_BASE_URL}/public_transport_routes"
