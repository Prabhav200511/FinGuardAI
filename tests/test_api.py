import json

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


def test_model_metrics_include_frontend_fields(tmp_path, monkeypatch) -> None:
    metrics_dir = tmp_path / "models"
    metrics_dir.mkdir()
    (metrics_dir / "params.json").write_text(
        json.dumps({
            "training_rows": 1200,
            "test_rows": 300,
            "threshold": 60.25,
            "input_features": ["amount", "merchant_category"],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(api, "MODEL_DIR", metrics_dir)

    client = TestClient(api.app)
    response = client.get("/model/metrics")

    assert response.status_code == 200
    body = response.json()
    assert body["total_processed"] == 1500
    assert body["current_threshold"] == 60.25
    assert isinstance(body["feature_importance"], list)


def test_demo_feed_marks_synthetic_fraud_transactions(monkeypatch) -> None:
    class StubPredictor:
        def predict(self, txn):
            return {"risk_score": 18.0, "is_fraud": False, "threshold": 60.0}

    monkeypatch.setattr(api, "_get_predictor", lambda: StubPredictor())
    monkeypatch.setattr(
        api,
        "generate_demo_batch",
        lambda n, fraud_ratio: [{
            "transaction_id": "demo-1",
            "amount": 50000,
            "hour": 1,
            "merchant_category": "electronics",
            "device_change": 1,
            "geo_distance_km": 1000,
            "velocity_per_hour": 8,
            "is_new_merchant": 1,
            "label": 1,
        }],
    )

    client = TestClient(api.app)
    response = client.get("/demo/feed?n=1&fraud_ratio=1.0")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["simulated_ground_truth"] == 1
    assert body[0]["is_fraud"] is True
