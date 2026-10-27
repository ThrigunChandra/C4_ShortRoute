from fastapi.testclient import TestClient

from app.services.url_services import generate_short_code
from app.main import app

client = TestClient(app)

def test_valid_url():
    response = client.post(
        "/api/links",
        json={
            "given_url":"https://example.com/articles"
        }
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["given_url"] == "https://example.com/articles"

    assert isinstance(body["short_code"], str)
    assert len(body["short_code"]) == 8

def test_invalid_url():
    response = client.post(
        "api/links",
        json = {
            "given_url" : "hello"
        }
    )
    assert response.status_code == 422