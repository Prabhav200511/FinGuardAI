"""
generate_data.py
Balanced Synthetic UPI Transaction Dataset Generator
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
    "grocery",
    "restaurant",
    "fuel",
    "clothing",
    "electronics",
    "pharmacy",
    "transport",
    "utilities",
    "education",
    "entertainment",
]

FRAUD_TYPES = [
    "late_night_high",
    "device_geo_jump",
    "velocity_attack",
    "social_engineering"
]

AMOUNT_BUCKETS = [
    (10, 500),
    (500, 2000),
    (2000, 8000),
    (8000, 30000),
    (30000, 150000)
]

GEO_BUCKETS = [
    (0, 1),
    (1, 5),
    (5, 20),
    (20, 100),
    (100, 500),
    (500, 1500)
]


def sample_bucket(bucket_list):
    low, high = random.choice(bucket_list)
    return round(random.uniform(low, high), 2)


def balanced_hours():
    return random.randint(0, 23)


def balanced_category(idx):
    return MERCHANT_CATEGORIES[idx % len(MERCHANT_CATEGORIES)]


def random_normal_txn(idx):
    return {
        "transaction_id": fake.uuid4(),

        "amount": sample_bucket(AMOUNT_BUCKETS),

        "hour": balanced_hours(),

        "merchant_category": balanced_category(idx),

        "device_change": random.randint(0, 1),

        "geo_distance_km": sample_bucket(GEO_BUCKETS),

        "velocity_per_hour": random.choice(
            [1, 2, 3, 4, 5, 6]
        ),

        "is_new_merchant": random.randint(0, 1),

        "label": 0,

        "fraud_pattern": "normal"
    }


def fraud_late_night_high():
    return {
        "amount": round(random.uniform(15000, 90000), 2),
        "hour": random.randint(0, 4),
        "device_change": 1,
        "geo_distance_km": round(random.uniform(200, 1200), 2),
        "velocity_per_hour": random.choice([1, 2]),
        "is_new_merchant": 1
    }


def fraud_device_geo_jump():
    return {
        "amount": round(random.uniform(5000, 50000), 2),
        "hour": random.randint(8, 22),
        "device_change": 1,
        "geo_distance_km": round(random.uniform(400, 1500), 2),
        "velocity_per_hour": random.choice([2, 3, 4]),
        "is_new_merchant": random.randint(0, 1)
    }


def fraud_velocity_attack():
    return {
        "amount": round(random.uniform(200, 8000), 2),
        "hour": random.randint(0, 23),
        "device_change": random.randint(0, 1),
        "geo_distance_km": round(random.uniform(0, 100), 2),
        "velocity_per_hour": random.choice([8, 12, 16, 20]),
        "is_new_merchant": random.randint(0, 1)
    }


def fraud_social_engineering():
    return {
        "amount": round(random.uniform(2000, 35000), 2),
        "hour": random.randint(9, 19),
        "device_change": random.randint(0, 1),
        "geo_distance_km": round(random.uniform(5, 80), 2),
        "velocity_per_hour": random.choice([1, 2, 3]),
        "is_new_merchant": 1
    }


def random_fraud_txn(idx):

    fraud_type = FRAUD_TYPES[idx % len(FRAUD_TYPES)]

    if fraud_type == "late_night_high":
        core = fraud_late_night_high()

    elif fraud_type == "device_geo_jump":
        core = fraud_device_geo_jump()

    elif fraud_type == "velocity_attack":
        core = fraud_velocity_attack()

    else:
        core = fraud_social_engineering()

    return {
        "transaction_id": fake.uuid4(),

        "merchant_category": balanced_category(idx),

        "label": 1,

        "fraud_pattern": fraud_type,

        **core
    }


def generate_dataset(
        n_normal=9000,
        n_fraud=1000,
        output_path=OUTPUT_PATH
):

    normal_rows = [
        random_normal_txn(i)
        for i in range(n_normal)
    ]

    fraud_rows = [
        random_fraud_txn(i)
        for i in range(n_fraud)
    ]

    rows = normal_rows + fraud_rows

    df = pd.DataFrame(rows)

    df = df.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    print("\nDataset Statistics")
    print("=" * 40)

    print("Total Rows:", len(df))
    print("Fraud Rows:", n_fraud)
    print("Normal Rows:", n_normal)

    print("\nFraud Distribution")
    print(df["fraud_pattern"].value_counts())

    print("\nMerchant Distribution")
    print(df["merchant_category"].value_counts())

    print("\nHour Distribution")
    print(df["hour"].value_counts().sort_index())

    print("\nSaved to:", output_path)

    return df


def generate_demo_batch(
        n=20,
        fraud_ratio=0.35
):

    n_fraud = int(n * fraud_ratio)
    n_normal = n - n_fraud

    batch = []

    for i in range(n_normal):
        batch.append(random_normal_txn(i))

    for i in range(n_fraud):
        batch.append(random_fraud_txn(i))

    random.shuffle(batch)

    return batch


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--normal",
        type=int,
        default=9000
    )

    parser.add_argument(
        "--fraud",
        type=int,
        default=1000
    )

    parser.add_argument(
        "--output",
        default=OUTPUT_PATH
    )

    args = parser.parse_args()

    generate_dataset(
        n_normal=args.normal,
        n_fraud=args.fraud,
        output_path=args.output
    )