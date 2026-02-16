from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_get_status_endpoint_returns_200():
    response = client.get("/status")
    assert response.status_code == 200

