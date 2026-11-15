from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

Nonnegative = Annotated[float, Field(ge=0, le=1e9, allow_inf_nan=False)]


class Sample(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ph: Annotated[float, Field(ge=0, le=14, allow_inf_nan=False)]
    Hardness: Nonnegative
    Solids: Nonnegative
    Chloramines: Nonnegative
    Sulfate: Nonnegative
    Conductivity: Nonnegative
    Organic_carbon: Nonnegative
    Trihalomethanes: Nonnegative
    Turbidity: Nonnegative


class ModelPrediction(BaseModel):
    id: str
    name: str
    predicted_class: int
    label: str
    potable_probability: float
    selected_class_probability: float


class Prediction(BaseModel):
    analysis_id: str
    created_at: str
    source: str
    measurements: Sample
    primary_model: str
    version: str
    predicted_class: int
    label: str
    selected_class_probability: float
    calibration: str
    models: list[ModelPrediction]
    agreement_count: int
    agreement_percentage: float
    parameters: list[dict[str, Any]]
    warnings: list[str]
    decision_path: list[str]
    disclaimer: str


class BatchResponse(BaseModel):
    batch_id: str
    total: int
    valid: int
    invalid: int
    potable: int
    non_potable: int
    results: list[dict[str, Any]]
    errors: list[dict[str, Any]]
