from pathlib import Path

import pytest

from generate_data import generate_dataset
from predictor import FraudPredictor
from train import train


@pytest.fixture(scope="session")
def trained_predictor(tmp_path_factory: pytest.TempPathFactory) -> FraudPredictor:
    root = tmp_path_factory.mktemp("model_fixture")
    data_path = root / "transactions.csv"
    model_dir = root / "models"
    generate_dataset(900, 100, str(data_path))
    train(data_path, model_dir, n_estimators=80, build_shap=False)
    return FraudPredictor(Path(model_dir))
