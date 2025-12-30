from fastapi import APIRouter
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib # Not using matplotlib but fixing the issue of multi thread problem when request overlapped
matplotlib.use('Agg')
from pathlib import Path
from utils.feature_extraction import extract_features_from_latlon
from utils.analysis import get_site_insights

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "backend"/"models" / "incinerator_rf_model.pkl"
TRAIN_DATA_PATH = BASE_DIR / "data" / "processed" / "selangor_training.csv"

# Load Model and Initialize SHAP
model = joblib.load(MODEL_PATH)
# We use a small sample of training data as a background for the explainer
background_data = pd.read_csv(TRAIN_DATA_PATH).drop(columns=['latitude', 'longitude', 'suitable']).sample(100)
explainer = shap.TreeExplainer(model)


@router.get("/predict")
def predict_site(latitude: float, longitude: float):
    # 1. Extract raw features
    features_dict = extract_features_from_latlon(latitude, longitude)
    
    # 2. Format for Model
    input_data = np.array([[
        features_dict["population"],
        features_dict["land_use"],
        features_dict["dist_river_m"],
        features_dict["dist_road_m"]
    ]])
    
    # 3. Get Prediction
    prediction = int(model.predict(input_data)[0])
    
    # 4. Calculate SHAP values (XAI)
    # This explains why the model gave this specific prediction
    shap_values = explainer.shap_values(input_data)

    # Handle different SHAP return formats
    if isinstance(shap_values, list):
        # For older SHAP versions or certain classifiers, it returns a list [class0, class1]
        # We want class 1 (Suitable)
        impacts = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
    else:
        # For newer SHAP versions, it often returns a single array or Explanation object
        # If the shape is (1, 4), it's already the impacts for the single prediction
        if len(shap_values.shape) == 3: # (samples, features, classes)
            impacts = shap_values[0, :, 1]
        else:
            impacts = shap_values[0]

    return {
        "prediction": "Suitable" if prediction == 1 else "Not Suitable",
        "features": features_dict,
        "shap_explanation": {
            "population": float(impacts[0]),
            "land_use": float(impacts[1]),
            "dist_river_m": float(impacts[2]),
            "dist_road_m": float(impacts[3])
        },
        "insights": get_site_insights(features_dict)
    }