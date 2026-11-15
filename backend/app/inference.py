import json
import os
import pickle
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
from fastapi import HTTPException

from backend.app.schemas import Prediction, Sample
from backend.app.standards import check_parameters
from ml.data import FEATURES, ROOT

DISCLAIMER = (
    "Educational screening estimate only. Model probability is not the probability that water is safe. "
    "Laboratory testing, including microbial and other contaminants, is required before consumption."
)


class Registry:
    def __init__(self, directory=None):
        self.directory = Path(directory or os.getenv("JALSATHI_ARTIFACTS", ROOT / "ml/artifacts"))
        self.metadata = None
        self.models = {}
        self.error = None
        try:
            self.metadata = json.loads((self.directory / "registry.json").read_text(encoding="utf-8"))
            for item in self.metadata["models"]:
                # Only locally generated, trusted artifacts; never accept uploaded pickle files.
                self.models[item["id"]] = joblib.load(self.directory / f"{item['id']}.joblib")
        except (OSError, ValueError, KeyError, ImportError, EOFError, pickle.UnpicklingError) as exc:
            self.error = type(exc).__name__
            self.models = {}

    def require(self):
        if len(self.models) != 5 or not self.metadata:
            raise HTTPException(
                503, "Trained models unavailable. Run python -m ml.train and restart the API."
            )

    def predict_many(self, samples: list[Sample], source="single"):
        self.require()
        frame = pd.DataFrame([s.model_dump() for s in samples], columns=FEATURES)
        probabilities = {key: model.predict_proba(frame)[:, 1] for key, model in self.models.items()}
        cart = self.models["cart"]
        transformed = cart.named_steps["imputer"].transform(frame)
        tree = cart.named_steps["model"].tree_
        paths = cart.named_steps["model"].decision_path(transformed)
        results = []
        for row, sample in enumerate(samples):
            values = sample.model_dump()
            predictions = []
            for item in self.metadata["models"]:
                p = float(probabilities[item["id"]][row])
                cls = int(p >= 0.5)
                predictions.append(
                    dict(
                        id=item["id"],
                        name=item["name"],
                        predicted_class=cls,
                        label="Predicted Potable" if cls else "Predicted Non-Potable",
                        potable_probability=p,
                        selected_class_probability=p if cls else 1 - p,
                    )
                )
            primary = next(p for p in predictions if p["id"] == self.metadata["primary"])
            agreement = sum(p["predicted_class"] == primary["predicted_class"] for p in predictions)
            warnings = [
                "Eight mass/unit-based reference comparisons are unavailable; dataset units are unverified.",
                "Microbial and other essential safety tests are missing. No drinking-water certification.",
            ]
            for c, (lo, hi) in self.metadata["training_ranges"].items():
                if not lo <= values[c] <= hi:
                    warnings.append(f"{c}: outside observed training range [{lo:.3g}, {hi:.3g}].")
            parameters = check_parameters(values)
            if parameters[0]["status"] == "outside":
                warnings.append(
                    "pH is outside the EPA secondary reference range; a positive model result does not override this."
                )
            nodes = paths.indices[paths.indptr[row] : paths.indptr[row + 1]]
            path = []
            for node in nodes:
                feature = tree.feature[node]
                if feature >= 0:
                    value = transformed[row, feature]
                    op = "≤" if value <= tree.threshold[node] else ">"
                    path.append(f"{FEATURES[feature]} {value:.3f} {op} {tree.threshold[node]:.3f}")
            results.append(
                Prediction(
                    analysis_id=str(uuid4()),
                    created_at=datetime.now(timezone.utc).isoformat(),
                    source=source,
                    measurements=sample,
                    primary_model=self.metadata["primary"],
                    version=self.metadata["version"],
                    predicted_class=primary["predicted_class"],
                    label=primary["label"],
                    selected_class_probability=primary["selected_class_probability"],
                    calibration="Uncalibrated",
                    models=predictions,
                    agreement_count=agreement,
                    agreement_percentage=agreement / 5 * 100,
                    parameters=parameters,
                    warnings=warnings,
                    decision_path=path,
                    disclaimer=DISCLAIMER,
                ).model_dump()
            )
        return results
