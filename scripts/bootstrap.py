"""Create a local virtual environment, install dependencies, and train the model."""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    if not VENV.exists():
        venv.EnvBuilder(with_pip=True).create(VENV)

    python = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python), "-m", "pip", "install", "-r", "requirements-dev.txt"])
    run([str(python), "generate_data.py"])
    run([str(python), "train.py"])
    run([str(python), "-m", "pytest"])
    print("\nReady. Run:")
    print(f"  {python} -m streamlit run app.py")
    print(f"  {python} -m uvicorn api:app --reload")


if __name__ == "__main__":
    main()
