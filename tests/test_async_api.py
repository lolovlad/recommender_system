from fastapi.testclient import TestClient
from src.presentation.api import app

client = TestClient(app)


def test_async_recommendation_flow():
    response = client.post(
        "/api/v1/recommendations/generate_for_user",
        json={"user_id": 1}
    )

    assert response.status_code == 202
    assert "task_id" in response.json()