from fastapi.testclient import TestClient
from src.recommender_system.presentation.api import app

client = TestClient(app)


def test_estimate_delivery_time_success():
    payload = {
        "distance_km": 6.0,
        "hour": 15,
        "day_of_week": 3,
        "items_count": 4
    }

    response = client.post(
        "/api/v1/delivery/estimate_time",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "estimated_minutes" in data
    assert isinstance(data["estimated_minutes"], float)
    assert data["estimated_minutes"] > 0