# services/prediction_service.py
import joblib
import numpy as np
from pathlib import Path
from services.feature_extraction_service import FeatureExtractionService


class PredictionService:
    """Handles ML model predictions."""
    
    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        MODEL_PATH = BASE_DIR / "backend" / "models" / "incinerator_rf_model.pkl"
        self.model = joblib.load(MODEL_PATH)
        self.feature_extractor = FeatureExtractionService()
    
    def extract_features(self, latitude: float, longitude: float) -> dict:
        """Extract features from coordinates."""
        return self.feature_extractor.extract_features(latitude, longitude)
    
    def predict(self, features: dict) -> str:
        """Make prediction using ML model."""
        input_data = np.array([[
            features["population"],
            features["land_use"],
            features["dist_river_m"],
            features["dist_road_m"]
        ]])
        
        prediction = int(self.model.predict(input_data)[0])
        return "Suitable" if prediction == 1 else "Not Suitable"


# services/scoring_service.py
from typing import Dict