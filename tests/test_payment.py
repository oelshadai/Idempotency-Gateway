from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_first_payment():
    response = client.post(
        "/process-payment",
        headers={"Idempotency-Key": "abc123"},
        json={"amount": 100, "currency": "GHS"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Charged 100 GHS"

def test_duplicate_payment():
    # first request
    client.post(
        "/process-payment",
        headers={"Idempotency-Key": "dup123"},
        json={"amount": 50, "currency": "GHS"}
    )

    # second request
    response = client.post(
        "/process-payment",
        headers={"Idempotency-Key": "dup123"},
        json={"amount": 50, "currency": "GHS"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Charged 50 GHS"
    assert response.headers.get("X-Cache-Hit") == "true"

def test_conflict_different_payload():
    client.post(
        "/process-payment",
        headers={"Idempotency-Key": "fraud123"},
        json={"amount": 100, "currency": "GHS"}
    )

    response = client.post(
        "/process-payment",
        headers={"Idempotency-Key": "fraud123"},
        json={"amount": 500, "currency": "GHS"}
    )

    assert response.status_code == 409
    assert "error" in response.json()

def test_missing_idempotency_key():
    response = client.post(
        "/process-payment",
        json={"amount": 100, "currency": "GHS"}
    )

    assert response.status_code == 400
