# models/prediction_models.py
from pydantic import BaseModel, Field
from typing import Dict, List, Any


class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    weights: Dict[str, float] = Field(
        default={'pop': 0.25, 'river': 0.25, 'road': 0.25, 'land': 0.25}
    )


class Features(BaseModel):
    population: float
    land_use: int
    dist_river_m: float
    dist_road_m: float

class Insight(BaseModel):
    """Individual site insight with text and severity level."""
    text: str
    level: str

class PredictionResponse(BaseModel):
    prediction: str
    policy_score: float
    features: Dict
    shap_explanation: Dict[str, float]
    insights: List[Dict[str, str]]