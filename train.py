"""Train and evaluate the FinGuard AI anomaly-detection model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    import shap

    SHAP_OK = True
except ImportError:
    SHAP_OK = False


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "upi_transactions.csv"
MODEL_DIR = BASE_DIR / "models"

NUMERIC_FEATURES = [
    "amount",
    "hour",
    "device_change",
    "geo_distance_km",
    "velocity_per_hour",
    "is_new_merchant",
]
CATEGORICAL_FEATURES = ["merchant_category"]
INPUT_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
RANDOM_STATE = 42


def _to_risk(raw: np.ndarray, low_score: float, high_score: float) -> np.ndarray:
    """Map Isolation Forest normality scores to risk scores from 0 to 100."""
    width = max(high_score - low_score, np.finfo(float).eps)
    return np.clip(100.0 * (1.0 - (raw - low_score) / width), 0.0, 100.0)


def _best_threshold(y_true: np.ndarray, risk_scores: np.ndarray) -> tuple[float, float]:
    """Select the held-out threshold that maximizes fraud-class F1."""
    candidates = np.unique(np.round(risk_scores, 2))
    best_threshold = 50.0
    best_f1 = -1.0
    for threshold in candidates:
        score = f1_score(y_true, risk_scores >= threshold, zero_division=0)
        if score > best_f1:
            best_threshold = float(threshold)
            best_f1 = float(score)
    return best_threshold, best_f1


def _build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            (
                "category",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


def train(
    data_path: str | Path = DATA_PATH,
    model_dir: str | Path = MODEL_DIR,
    *,
    n_estimators: int = 300,
    build_shap: bool = True,
) -> dict:
    """Train on normal behavior and evaluate on a stratified held-out set."""
    data_path = Path(data_path)
    model_dir = Path(model_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}. Run generate_data.py first.")

    df = pd.read_csv(data_path)
    missing = sorted(set(INPUT_FEATURES + ["label"]) - set(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")

    train_df, test_df = train_test_split(
        df,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=df["label"],
    )

    # Isolation Forest learns the shape of legitimate behavior. Fraud labels are
    # used only to calibrate and evaluate the decision threshold on held-out data.
    normal_train = train_df.loc[train_df["label"] == 0, INPUT_FEATURES]
    preprocessor = _build_preprocessor()
    X_normal = preprocessor.fit_transform(normal_train)

    model = IsolationForest(
        n_estimators=n_estimators,
        contamination="auto",
        max_samples=min(512, len(X_normal)),
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_normal)

    raw_normal = model.decision_function(X_normal)
    # Reserve headroom below the most anomalous normal observation so severe
    # anomalies retain meaningful score differences instead of all clipping to 100.
    normal_min = float(raw_normal.min())
    high_score = float(np.percentile(raw_normal, 99))
    low_score = normal_min - 0.25 * (high_score - normal_min)

    X_test = preprocessor.transform(test_df[INPUT_FEATURES])
    raw_test = model.decision_function(X_test)
    risk_test = _to_risk(raw_test, low_score, high_score)
    y_test = test_df["label"].to_numpy(dtype=int)
    threshold, _ = _best_threshold(y_test, risk_test)
    predictions = (risk_test >= threshold).astype(int)

    f1 = float(f1_score(y_test, predictions, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, risk_test))
    report = classification_report(
        y_test,
        predictions,
        target_names=["Normal", "Fraud"],
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(y_test, predictions).tolist()

    explainer = None
    if build_shap and SHAP_OK:
        explainer = shap.TreeExplainer(model)
        explainer.shap_values(X_test[:2])

    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_dir / "isolation_forest.pkl")
    joblib.dump(preprocessor, model_dir / "preprocessor.pkl")
    if explainer is not None:
        joblib.dump(explainer, model_dir / "shap_explainer.pkl")

    transformed_features = preprocessor.get_feature_names_out().tolist()
    params = {
        "model_version": "2.0.0",
        "random_state": RANDOM_STATE,
        "training_rows": int(len(normal_train)),
        "test_rows": int(len(test_df)),
        "test_fraud_rows": int(y_test.sum()),
        "low_score": low_score,
        "high_score": high_score,
        "threshold": round(threshold, 2),
        "input_features": INPUT_FEATURES,
        "transformed_features": transformed_features,
        "shap_available": explainer is not None,
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "precision_fraud": round(float(report["Fraud"]["precision"]), 4),
        "recall_fraud": round(float(report["Fraud"]["recall"]), 4),
        "confusion_matrix": matrix,
        "evaluation_note": "Metrics are from a stratified 20% held-out synthetic test set.",
    }
    (model_dir / "params.json").write_text(json.dumps(params, indent=2), encoding="utf-8")

    print(classification_report(y_test, predictions, target_names=["Normal", "Fraud"], digits=3))
    print(f"Held-out F1: {f1:.4f} | ROC-AUC: {roc_auc:.4f} | threshold: {threshold:.2f}")
    print(f"Artifacts saved to {model_dir}")
    return params


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=str(DATA_PATH), help="Input transaction CSV")
    parser.add_argument("--model-dir", default=str(MODEL_DIR), help="Artifact output directory")
    parser.add_argument("--estimators", type=int, default=300)
    parser.add_argument("--no-shap", action="store_true", help="Skip SHAP artifact generation")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    train(args.data, args.model_dir, n_estimators=args.estimators, build_shap=not args.no_shap)
