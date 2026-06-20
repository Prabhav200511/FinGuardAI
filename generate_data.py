"""
generate_data.py — Synthetic UPI Transaction Dataset Generator
FinGuard AI  |  10K realistic UPI transactions with injected fraud patterns
Usage: python generate_data.py
"""

import argparse
import os
import random
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "upi_transactions.csv")

MERCHANT_CATEGORIES = [
    "grocery", "restaurant", "fuel", "clothing", "electronics",
    "pharmacy", "transport", "utilities", "education", "entertainment",
]

# Hour-of-day distribution: peak 9 AM–8 PM, tails at night
_HOUR_W = np.array([
    0.010, 0.008, 0.006, 0.005, 0.005, 0.010,  # 00-05
    0.020, 0.030, 0.045, 0.065, 0.070, 0.075,  # 06-11
    0.075, 0.070, 0.065, 0.060, 0.055, 0.055,  # 12-17
    0.050, 0.045, 0.040, 0.035, 0.025, 0.015,  # 18-23
], dtype=float)
_HOUR_W /= _HOUR_W.sum()


# ── Single-transaction generators ────────────────────────────────────────────

def random_normal_txn() -> dict:
    """Generate one plausible, legitimate UPI transaction."""
    return {
        "transaction_id":   fake.uuid4(),
        "amount":           round(float(np.clip(np.random.lognormal(5.5, 1.0), 10, 150_000)), 2),
        "hour":             int(np.random.choice(24, p=_HOUR_W)),
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "device_change":    int(random.random() < 0.04),
        "geo_distance_km":  round(float(max(np.random.exponential(3.5), 0.0)), 2),
        "velocity_per_hour": random.choices([1, 2, 3, 4], weights=[0.60, 0.25, 0.10, 0.05])[0],
        "is_new_merchant":  int(random.random() < 0.08),
        "label":            0,
        "fraud_pattern":    "normal",
    }


def random_fraud_txn() -> dict:
    """Generate one fraudulent UPI transaction (one of four attack patterns)."""
    fraud_type = random.choices(
        ["late_night_high", "device_geo_jump", "velocity_attack", "social_engineering"],
        weights=[0.30, 0.30, 0.25, 0.15],
    )[0]

    if fraud_type == "late_night_high":
        # Late-night, large-amount, new device, far location
        core = dict(
            hour=random.choice([0, 1, 2, 3, 4]),
            amount=round(random.uniform(15_000, 90_000), 2),
            device_change=int(random.random() < 0.82),
            geo_distance_km=round(random.uniform(200, 1_200), 2),
            velocity_per_hour=random.choice([1, 2]),
            is_new_merchant=int(random.random() < 0.90),
        )
    elif fraud_type == "device_geo_jump":
        # Device switch paired with large geographic jump
        core = dict(
            hour=random.randint(8, 22),
            amount=round(random.uniform(5_000, 50_000), 2),
            device_change=1,
            geo_distance_km=round(random.uniform(400, 1_500), 2),
            velocity_per_hour=random.choices([2, 3, 4], weights=[0.3, 0.4, 0.3])[0],
            is_new_merchant=int(random.random() < 0.70),
        )
    elif fraud_type == "velocity_attack":
        # Rapid-fire transactions in a short window
        core = dict(
            hour=random.randint(0, 23),
            amount=round(random.uniform(200, 8_000), 2),
            device_change=int(random.random() < 0.50),
            geo_distance_km=round(random.uniform(0, 100), 2),
            velocity_per_hour=random.choices([8, 12, 16, 20], weights=[0.30, 0.30, 0.25, 0.15])[0],
            is_new_merchant=int(random.random() < 0.40),
        )
    else:  # social_engineering
        # Phishing-induced payment to an unknown merchant
        core = dict(
            hour=random.randint(9, 19),
            amount=round(random.uniform(2_000, 35_000), 2),
            device_change=int(random.random() < 0.25),
            geo_distance_km=round(random.uniform(5, 80), 2),
            velocity_per_hour=random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0],
            is_new_merchant=1,
        )

    return {
        "transaction_id":    fake.uuid4(),
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "label": 1,
        "fraud_pattern": fraud_type,
        **core,
    }


# ── Batch generators ──────────────────────────────────────────────────────────

def generate_dataset(
    n_normal: int = 9_000,
    n_fraud: int = 1_000,
    output_path: str = OUTPUT_PATH,
) -> pd.DataFrame:
    """Generate full training dataset and save to CSV."""
    rows = [random_normal_txn() for _ in range(n_normal)] + \
           [random_fraud_txn()  for _ in range(n_fraud)]
    df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df):,} transactions "
          f"({n_fraud} fraud | {n_fraud / len(df) * 100:.1f}%) -> {output_path}")
    return df


def generate_demo_batch(n: int = 20, fraud_ratio: float = 0.35) -> list:
    """Return a mixed batch for the live dashboard demo feed."""
    n_fraud  = round(n * fraud_ratio)
    n_normal = n - n_fraud
    batch    = [random_normal_txn() for _ in range(n_normal)] + \
               [random_fraud_txn()  for _ in range(n_fraud)]
    random.shuffle(batch)
    return batch


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normal", type=int, default=9_000)
    parser.add_argument("--fraud", type=int, default=1_000)
    parser.add_argument("--output", default=OUTPUT_PATH)
    args = parser.parse_args()
    generate_dataset(args.normal, args.fraud, args.output)
