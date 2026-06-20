from fastapi.testclient import TestClient

import api


PAYLOAD = {
    "amount": 45000,
    "hour": 2,
    "merchant_category": "electronics",
    "device_change": 1,
    "geo_distance_km": 850,
    "velocity_per_hour": 2,
    "is_new_merchant": 1,
    "language": "english",
}


def test_predict_endpoint(monkeypatch, trained_predictor) -> None:
    monkeypatch.setattr(api, "_get_predictor", lambda: trained_predictor)
    client = TestClient(api.app)
    response = client.post("/predict", json=PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["risk_score"] <= 100
    assert body["is_fraud"] is True


def test_validation_rejects_bad_hour() -> None:
    client = TestClient(api.app)
    response = client.post("/predict", json={**PAYLOAD, "hour": 25})
    assert response.status_code == 422
