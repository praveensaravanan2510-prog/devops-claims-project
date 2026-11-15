import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health_returns_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_claim_is_processed(client):
    res = client.get("/claims/ca/12345")
    body = res.get_json()
    assert res.status_code == 200
    assert body["stateId"] == "CA"
    assert body["generatedFile"] == "claim_CA_12345.edi"


def test_invalid_input_returns_400(client):
    res = client.get("/claims/california/abc")
    assert res.status_code == 400


def test_metrics_endpoint_exposes_request_counter(client):
    client.get("/health")
    res = client.get("/metrics")
    assert res.status_code == 200
    assert b"http_requests_total" in res.data
