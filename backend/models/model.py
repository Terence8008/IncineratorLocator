import joblib
import numpy as np
from pathlib import Path


MODEL_PATH = Path(__file__).resolve().parent / "incinerator_rf_model.pkl"

class IncineratorPredictor:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)

    def predict(self, features):
        """
        features = [
            population,
            land_use,
            dist_river,
            dist_road
        ]
        """
        arr = np.array(features).reshape(1, -1)
        return float(self.model.predict(arr)[0])
