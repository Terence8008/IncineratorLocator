from fastapi import APIRouter
from models.model import IncineratorPredictor
from utils.feature_extraction import extract_features_from_latlon
from utils.analysis import get_site_insights
import numpy as np

router = APIRouter()
model = IncineratorPredictor()

@router.get("/predict")
def predict(latitude: float, longitude: float):
    features_dict = extract_features_from_latlon(latitude, longitude)

    # Convert all values in features_dict to native Python types
    features_dict = {k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                     for k, v in features_dict.items()}
    
    # Prepare features list for model
    features_list = [
        features_dict["population"],
        features_dict["land_use"],
        features_dict["dist_river_m"],
        features_dict["dist_road_m"]
    ]
    
    # Prediction as native int
    prediction = int(model.predict(features_list))

    #Get Human-Readable Analysis
    insights = get_site_insights(features_dict)

    return {
        "lat": float(latitude),
        "lon": float(longitude),
        "features": features_dict,
        "prediction": "Suitable" if prediction == 1 else "Not Suitable",
        "insights": insights
    }
