from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Successful Redirect
def test_successful_redirect():
    code = 'hello303'

    response = client.get(
        f"/{code}",
        follow_redirects=False
    )

    assert response.status_code == 302, response.text
    assert response.headers['location'] == "https://www.instagram.com/_thrigun"

# Expired Link 
def test_expired_link():
    code = "xyn3R7aM"

    response = client.get(
        f'/{code}',
        follow_redirects = False
    )

    assert response.status_code == 410, response.text 


