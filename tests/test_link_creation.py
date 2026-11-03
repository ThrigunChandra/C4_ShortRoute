from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Shortening
def test_valid_url():
    response = client.post(
        "/api/links",
        json={"given_url" : "https://example.com/videos"}
    )

    assert response.status_code == 201, response.text

    body = response.json()

    assert len(body["short_code"]) == 8
    assert isinstance(body["short_code"], str)
    assert body['short_url'] == f"http://127.0.0.1:8000/{body['short_code']}"

# Testing with different inputss
def test_invalid_url():
    response = client.post(
        "api/links",
        json = {
            "given_url" : "hello"
        }
    )
    assert response.status_code == 422