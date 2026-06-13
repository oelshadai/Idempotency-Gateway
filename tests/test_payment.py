import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_first_payment(client):
    response = client.post(
        "/process-payment",
        headers={"Idempotency-Key": "abc123"},
        json={"amount": 100, "currency": "GHS"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Charged 100 GHS"


def test_duplicate_payment(client):
    # first request
    client.post(
        "/process-payment",
        headers={"Idempotency-Key": "dup123"},
        json={"amount": 50, "currency": "GHS"}
    )

    # second request - same key same body
    response = client.post(
        "/process-payment",
        headers={"Idempotency-Key": "dup123"},
        json={"amount": 50, "currency": "GHS"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Charged 50 GHS"
    assert response.headers.get("X-Cache-Hit") == "true"


def test_conflict_different_payload(client):
    # first request
    client.post(
        "/process-payment",
        headers={"Idempotency-Key": "fraud123"},
        json={"amount": 100, "currency": "GHS"}
    )

    # second request - same key DIFFERENT body
    response = client.post(
        "/process-payment",
        headers={"Idempotency-Key": "fraud123"},
        json={"amount": 500, "currency": "GHS"}
    )

    assert response.status_code == 409
    assert "error" in response.get_json()


def test_missing_idempotency_key(client):
    response = client.post(
        "/process-payment",
        json={"amount": 100, "currency": "GHS"}
    )

    assert response.status_code == 400