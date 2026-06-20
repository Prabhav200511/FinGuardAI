from groq_client import get_explanation


TXN = {"amount": 45000, "hour": 2}
PRED = {
    "risk_score": 92,
    "top_features": [
        {
            "feature": "geo_distance_km",
            "label_en": "Distance from last transaction",
            "display_value": "850.0 km",
            "increases_risk": True,
        },
        {
            "feature": "device_change",
            "label_en": "New or changed device",
            "display_value": "Yes",
            "increases_risk": True,
        },
    ],
}


def test_offline_english_explanation_uses_transaction_features(monkeypatch) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    text = get_explanation(TXN, PRED, "english")
    assert "850.0 km" in text
    assert "new or changed device" in text


def test_offline_hindi_explanation_is_hindi(monkeypatch) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    text = get_explanation(TXN, PRED, "hindi")
    assert "लेनदेन" in text
    assert "बैंक" in text
