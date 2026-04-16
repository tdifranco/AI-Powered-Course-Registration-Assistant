from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_courses(path: str | None = None) -> pd.DataFrame:
    csv_path = Path(path) if path else DATA_DIR / "courses.csv"
    df = pd.read_csv(csv_path)
    df = df.fillna("")
    return df


def load_students(path: str | None = None) -> list[dict]:
    json_path = Path(path) if path else DATA_DIR / "sample_students.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_categories(path: str | None = None) -> dict:
    json_path = Path(path) if path else DATA_DIR / "categories.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_degree_requirements(path: str | None = None) -> dict:
    json_path = Path(path) if path else DATA_DIR / "degree_requirements.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
