"""Schema checks shared by reproducible training and tests."""

import hashlib
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FEATURES = [
    "ph",
    "Hardness",
    "Solids",
    "Chloramines",
    "Sulfate",
    "Conductivity",
    "Organic_carbon",
    "Trihalomethanes",
    "Turbidity",
]
SEED = 42
SOURCE = "https://www.kaggle.com/datasets/adityakadiwal/water-potability"


def load_dataset(path=None):
    path = Path(path or os.getenv("JALSATHI_DATASET", ROOT / "water_potability.csv"))
    frame = pd.read_csv(path)
    if list(frame.columns) != FEATURES + ["Potability"]:
        raise ValueError("Dataset columns must match the original nine features and Potability.")
    if not all(pd.api.types.is_numeric_dtype(frame[c]) for c in frame):
        raise ValueError("Dataset columns must be numeric.")
    if np.isinf(frame.to_numpy()).any():
        raise ValueError("Infinite dataset values are not supported.")
    if frame.Potability.isna().any() or set(frame.Potability.unique()) != {0, 1}:
        raise ValueError("Potability must contain both binary classes without missing labels.")
    if frame[FEATURES].isna().all().any():
        raise ValueError("A feature is entirely missing.")
    return frame, hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(frame, fingerprint):
    outliers = {}
    for c in FEATURES:
        q1, q3 = frame[c].quantile([0.25, 0.75])
        outliers[c] = int(((frame[c] < q1 - 1.5 * (q3 - q1)) | (frame[c] > q3 + 1.5 * (q3 - q1))).sum())
    return dict(
        rows=len(frame),
        features=FEATURES,
        source=SOURCE,
        sha256=fingerprint,
        missing=frame.isna().sum().to_dict(),
        duplicates=int(frame.duplicated().sum()),
        classes={str(k): int(v) for k, v in frame.Potability.value_counts().items()},
        statistics=frame[FEATURES].describe().to_dict(),
        outliers_iqr=outliers,
        negative_values=(frame[FEATURES] < 0).sum().to_dict(),
        limitations=[
            "Collection locations and label verification are not independently established.",
            "Dataset measurement units have not been independently verified.",
            "No comprehensive microbial, metal, pesticide or radiological testing.",
        ],
    )
