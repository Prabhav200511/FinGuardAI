from predictor import FraudPredictor


SAFE = {
    "amount": 250,
    "hour": 14,
    "merchant_category": "grocery",
    "device_change": 0,
    "geo_distance_km": 1.5,
    "velocity_per_hour": 1,
    "is_new_merchant": 0,
}

SUSPICIOUS = {
    "amount": 65000,
    "hour": 2,
    "merchant_category": "electronics",
    "device_change": 1,
    "geo_distance_km": 900,
    "velocity_per_hour": 2,
    "is_new_merchant": 1,
}


def test_suspicious_transaction_scores_above_safe(trained_predictor: FraudPredictor) -> None:
    safe = trained_predictor.predict(SAFE)
    suspicious = trained_predictor.predict(SUSPICIOUS)
    assert suspicious["risk_score"] > safe["risk_score"]
    assert suspicious["is_fraud"] is True
    assert len(suspicious["top_features"]) == 3


def test_missing_field_is_rejected(trained_predictor: FraudPredictor) -> None:
    invalid = dict(SAFE)
    invalid.pop("amount")
    try:
        trained_predictor.predict(invalid)
    except ValueError as exc:
        assert "amount" in str(exc)
    else:
        raise AssertionError("Expected a missing-field ValueError")
