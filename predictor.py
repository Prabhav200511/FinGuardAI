"""Real-time fraud inference and SHAP feature aggregation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import ClassVar

import joblib
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path(os.getenv("FINGUARD_MODEL_DIR", BASE_DIR / "models"))
NUMERIC_FEATURES = [
    "amount",
    "hour",
    "device_change",
    "geo_distance_km",
    "velocity_per_hour",
    "is_new_merchant",
]
INPUT_FEATURES = NUMERIC_FEATURES + ["merchant_category"]

FEATURE_META = {
    "amount": {
        "en": "Transaction amount",
        "hi": "लेनदेन राशि",
        "fmt": lambda v: f"₹{float(v):,.0f}",
    },
    "hour": {
        "en": "Time of transaction",
        "hi": "लेनदेन का समय",
        "fmt": lambda v: f"{int(v):02d}:00",
    },
    "device_change": {
        "en": "New or changed device",
        "hi": "नया या बदला उपकरण",
        "fmt": lambda v: "Yes" if int(v) else "No",
    },
    "geo_distance_km": {
        "en": "Distance from last transaction",
        "hi": "पिछले लेनदेन से दूरी",
        "fmt": lambda v: f"{float(v):.1f} km",
    },
    "velocity_per_hour": {
        "en": "Transactions per hour",
        "hi": "प्रति घंटे लेनदेन",
        "fmt": lambda v: str(int(v)),
    },
    "is_new_merchant": {
        "en": "New merchant",
        "hi": "नया व्यापारी",
        "fmt": lambda v: "Yes" if int(v) else "No",
    },
    "merchant_category": {
        "en": "Merchant category",
        "hi": "व्यापारी श्रेणी",
        "fmt": lambda v: str(v).replace("_", " ").title(),
    },
}


class FraudPredictor:
    """Loads trained artifacts once per model directory and serves predictions."""

    _instances: ClassVar[dict[str, "FraudPredictor"]] = {}

    def __init__(self, model_dir: str | Path = MODEL_DIR):
        self.model_dir = Path(model_dir).resolve()
        self.model = joblib.load(self.model_dir / "isolation_forest.pkl")
        self.preprocessor = joblib.load(self.model_dir / "preprocessor.pkl")
        self.explainer = None

        explainer_path = self.model_dir / "shap_explainer.pkl"
        if explainer_path.exists():
            self.explainer = joblib.load(explainer_path)

        self.params = json.loads((self.model_dir / "params.json").read_text(encoding="utf-8"))
        self.low_score = float(self.params["low_score"])
        self.high_score = float(self.params["high_score"])
        self.threshold = float(self.params["threshold"])
        self.transformed_features = self.params["transformed_features"]

    @classmethod
    def instance(cls, model_dir: str | Path = MODEL_DIR) -> "FraudPredictor":
        key = str(Path(model_dir).resolve())
        if key not in cls._instances:
            cls._instances[key] = cls(key)
        return cls._instances[key]

    def _risk_score(self, raw: float) -> float:
        width = max(self.high_score - self.low_score, np.finfo(float).eps)
        return float(np.clip(100.0 * (1.0 - (raw - self.low_score) / width), 0.0, 100.0))

    def _shap_row(self, transformed: np.ndarray) -> np.ndarray:
        if self.explainer is None:
            return np.zeros(len(self.transformed_features), dtype=float)
        values = self.explainer.shap_values(transformed)
        if isinstance(values, list):
            values = values[0]
        values = np.asarray(values)
        return values[0] if values.ndim > 1 else values

    def _aggregate_contributions(self, txn: dict, shap_row: np.ndarray) -> list[dict]:
        grouped = {feature: 0.0 for feature in INPUT_FEATURES}
        for transformed_name, value in zip(self.transformed_features, shap_row):
            if transformed_name.startswith("numeric__"):
                feature = transformed_name.removeprefix("numeric__")
            else:
                feature = "merchant_category"
            grouped[feature] += float(value)

        contributions = []
        for feature in INPUT_FEATURES:
            value = grouped[feature]
            meta = FEATURE_META[feature]
            raw_value = txn[feature]
            contributions.append(
                {
                    "feature": feature,
                    "label_en": meta["en"],
                    "label_hi": meta["hi"],
                    "raw_value": raw_value,
                    "display_value": meta["fmt"](raw_value),
                    "shap_value": round(value, 6),
                    # Lower Isolation Forest output means more anomalous.
                    "increases_risk": value < 0,
                }
            )
        contributions.sort(key=lambda item: abs(item["shap_value"]), reverse=True)
        return contributions

    def predict(self, txn: dict) -> dict:
        missing = [feature for feature in INPUT_FEATURES if feature not in txn]
        if missing:
            raise ValueError(f"Missing transaction fields: {', '.join(missing)}")

        row = {feature: [txn[feature]] for feature in INPUT_FEATURES}
        # ColumnTransformer uses column names, so a one-row DataFrame is intentional.
        import pandas as pd

        transformed = self.preprocessor.transform(pd.DataFrame(row))
        raw_score = float(self.model.decision_function(transformed)[0])
        risk_score = self._risk_score(raw_score)
        contributions = self._aggregate_contributions(txn, self._shap_row(transformed))

        if risk_score >= 80:
            risk_level = "critical"
        elif risk_score >= self.threshold:
            risk_level = "high"
        elif risk_score >= max(35, self.threshold - 20):
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "is_fraud": bool(risk_score >= self.threshold),
            "threshold": self.threshold,
            "raw_score": round(raw_score, 8),
            "top_features": contributions[:3],
            "all_features": contributions,
            "model_version": self.params.get("model_version", "unknown"),
        }
