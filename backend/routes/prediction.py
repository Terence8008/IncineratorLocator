from fastapi import APIRouter
from ..models import load_model, predict_from_coordinates
from ..spatial_utils import extract_features_from_latlon

router = APIRouter()

model = load_model()

@router.get("/predict")
def predict(lat: float, lon: float):
    features = extract_features_from_latlon(lat, lon)
    prediction = predict_from_coordinates(model, features)
    
    return {
        "lat": lat,
        "lon": lon,
        "features": features,
        "prediction": "Suitable" if prediction == 1 else "Not Suitable"
    }