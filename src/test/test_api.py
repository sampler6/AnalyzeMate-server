from main import app
from starlette.testclient import TestClient

client = TestClient(app)


def test_check_startup() -> None:
    response = client.get("/check_startup/")
    assert response.status_code == 200
    resp_json = response.json()
    assert isinstance(resp_json, dict)
    assert resp_json["description"] == "Application startup successfully completed"
