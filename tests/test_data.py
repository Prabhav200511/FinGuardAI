from generate_data import generate_demo_batch


def test_demo_batch_respects_zero_fraud_ratio() -> None:
    rows = generate_demo_batch(20, fraud_ratio=0)
    assert len(rows) == 20
    assert sum(row["label"] for row in rows) == 0


def test_demo_batch_has_required_schema() -> None:
    row = generate_demo_batch(1, fraud_ratio=1)[0]
    required = {
        "transaction_id",
        "amount",
        "hour",
        "merchant_category",
        "device_change",
        "geo_distance_km",
        "velocity_per_hour",
        "is_new_merchant",
        "label",
        "fraud_pattern",
    }
    assert required <= row.keys()
