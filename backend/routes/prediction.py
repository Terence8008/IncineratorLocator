# routes/prediction.py
from fastapi import APIRouter, Query
from services.prediction_service import PredictionService
from services.scoring_service import ScoringService
from services.explanation_service import ExplanationService
from models.prediction_model import PredictionRequest, PredictionResponse

router = APIRouter()

# Initialize services (consider using dependency injection)
prediction_service = PredictionService()
scoring_service = ScoringService()
explanation_service = ExplanationService()


@router.get("/predict", response_model=PredictionResponse)
def predict_site(
    latitude: float,
    longitude: float,
    w_pop: float = Query(0.25, ge=0, le=1, description="Weight for population factor"),
    w_river: float = Query(0.25, ge=0, le=1, description="Weight for river proximity"),
    w_road: float = Query(0.25, ge=0, le=1, description="Weight for road access"),
    w_land: float = Query(0.25, ge=0, le=1, description="Weight for land use")
):
    """
    Predict site suitability for incinerator placement.
    
    Combines ML prediction, policy scoring, and explainability to assess
    whether a location is suitable for industrial waste facility placement.
    """
    
    # Create request object
    request = PredictionRequest(
        latitude=latitude,
        longitude=longitude,
        weights={'pop': w_pop, 'river': w_river, 'road': w_road, 'land': w_land}
    )
    
    # Delegate to services
    features = prediction_service.extract_features(request.latitude, request.longitude)
    prediction = prediction_service.predict(features)
    policy_score = scoring_service.calculate_score(features, request.weights)
    explanation = explanation_service.explain(features)
    insights = explanation_service.get_insights(features)
    
    
    return PredictionResponse(
        prediction=prediction,
        policy_score=policy_score,
        features=features,
        shap_explanation=explanation,
        insights=insights
    )
