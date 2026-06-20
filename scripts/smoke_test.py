"""Exercise the API in process and print a judge-friendly smoke-test result."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient

from api import app


SUSPICIOUS = {
    "transaction_id": "SMOKE-001",
    "amount": 45000,
    "hour": 2,
    "merchant_category": "electronics",
    "device_change": 1,
    "geo_distance_km": 850,
    "velocity_per_hour": 2,
    "is_new_merchant": 1,
    "language": "english",
}


def main() -> None:
    client = TestClient(app)
    health = client.get("/health")
    health.raise_for_status()
    explained = client.post("/explain", json=SUSPICIOUS)
    explained.raise_for_status()
    body = explained.json()
    print("Health:", health.json())
    print("Risk:", body["risk_score"], body["risk_level"], "flagged=", body["is_fraud"])
    print("Explanation:", body["explanation"])


if __name__ == "__main__":
    main()
