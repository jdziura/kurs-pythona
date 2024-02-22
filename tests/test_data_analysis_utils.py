import pytest
from bus_project.data_analysis.utils import haversine


@pytest.mark.parametrize("lon1, lat1, lon2, lat2, expected_distance", [
    (0, 0, 0, 0, 0),            # Same point
    (0, 0, 180, 0, 20015),      # Antipodal points, PI time earth radius
    (0, 0, 0, 1, 111.195),      # Different points
])
def test_haversine(lon1, lat1, lon2, lat2, expected_distance):
    distance = haversine(lon1, lat1, lon2, lat2)
    assert pytest.approx(distance, rel=0.001) == expected_distance
