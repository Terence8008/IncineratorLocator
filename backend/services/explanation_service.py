import shap
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import joblib
from pathlib import Path
from typing import Dict, List


class InsightLevel:
    """Severity levels for site insights."""
    SUCCESS = "success"  # Green - positive indicator
    WARNING = "warning"  # Yellow - caution required
    DANGER = "danger"    # Red - critical issue


class Insight:
    """Individual site insight with text and severity level."""
    def __init__(self, text: str, level: str):
        self.text = text
        self.level = level


class ExplanationService:
    """Handles SHAP explanations and insights."""
    
    # Land use category mappings
    LAND_USE_LABELS = {
        1: "Agriculture", 
        2: "Paddy", 
        3: "Rural Res",
        4: "Urban Res", 
        5: "Commercial", 
        6: "Industrial",
        7: "Roads", 
        8: "Urban", 
        9: "City Core"
    }
    
    def __init__(self, model_path: str = None, train_data_path: str = None):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        
        # Use provided paths or defaults
        if model_path is None:
            model_path = BASE_DIR / "backend" / "models" / "incinerator_rf_model.pkl"
        if train_data_path is None:
            train_data_path = BASE_DIR / "data" / "processed" / "selangor_training.csv"
        
        # Load model directly instead of importing PredictionService
        model = joblib.load(model_path)
        
        # Initialize SHAP explainer
        background_data = pd.read_csv(train_data_path).drop(
            columns=['latitude', 'longitude', 'suitable']
        ).sample(100)
        self.explainer = shap.TreeExplainer(model)
    
    def explain(self, features: dict) -> Dict[str, float]:
        """Generate SHAP explanations for prediction."""
        import numpy as np
        
        input_data = np.array([[
            features["population"],
            features["land_use"],
            features["dist_river_m"],
            features["dist_road_m"]
        ]])
        
        shap_values = self.explainer.shap_values(input_data)
        
        # Extract impacts
        if isinstance(shap_values, list):
            impacts = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        else:
            impacts = shap_values[0, :, 1] if len(shap_values.shape) == 3 else shap_values[0]
        
        return {
            "population": float(impacts[0]),
            "land_use": float(impacts[1]),
            "dist_river_m": float(impacts[2]),
            "dist_road_m": float(impacts[3])
        }
    
    def get_insights(self, features: dict) -> List[Dict]:
        """
        Analyze spatial features and return human-readable insights.
        Returns list of insights with text and severity level.
        """
        insights = []
        
        # Population analysis
        insights.extend(self._analyze_population(features))
        
        # Water proximity analysis
        insights.extend(self._analyze_water_proximity(features))
        
        # Logistics and road access
        insights.extend(self._analyze_logistics(features))
        
        # Land use compatibility
        insights.extend(self._analyze_land_use(features))
        
        return insights
    
    def _analyze_population(self, features: dict) -> List[Dict]:
        """Analyze population density impacts."""
        pop = features.get("population", 0)
        
        if pop > 80:
            return [{
                "text": "High Population Density: Exceeds safe buffer zone for emissions.",
                "level": InsightLevel.DANGER
            }]
        elif pop > 20:
            return [{
                "text": "Moderate Population: Requires advanced filtration systems.",
                "level": InsightLevel.WARNING
            }]
        else:
            return [{
                "text": "Low Population: Minimal risk to residential areas.",
                "level": InsightLevel.SUCCESS
            }]
    
    def _analyze_water_proximity(self, features: dict) -> List[Dict]:
        """Analyze environmental protection concerns."""
        dist_river = features.get("dist_river_m", 0)
        
        if dist_river < 500:
            return [{
                "text": "Water Risk: Too close to rivers. High contamination risk.",
                "level": InsightLevel.DANGER
            }]
        elif dist_river < 1000:
            return [{
                "text": "Water Caution: Proximity to water requires strict runoff controls.",
                "level": InsightLevel.WARNING
            }]
        else:
            return [{
                "text": "Water Safety: Sufficient distance from major water bodies.",
                "level": InsightLevel.SUCCESS
            }]
    
    def _analyze_logistics(self, features: dict) -> List[Dict]:
        """Analyze road access and logistics."""
        dist_road = features.get("dist_road_m", 0)
        
        if dist_road > 200:
            return [{
                "text": "Logistics Issue: High cost for waste transport and access.",
                "level": InsightLevel.DANGER
            }]
        else:
            return [{
                "text": "Access Quality: Site is well-connected to the road network.",
                "level": InsightLevel.SUCCESS
            }]
    
    def _analyze_land_use(self, features: dict) -> List[Dict]:
        """Analyze land use compatibility."""
        lu_value = int(features.get("land_use", 0))
        label = self.LAND_USE_LABELS.get(lu_value, "Unknown")
        
        if lu_value == 9:
            return [{
                "text": f"Location: {label}. High-density city center. Strict regulations.",
                "level": InsightLevel.DANGER
            }]
        elif lu_value == 6:
            return [{
                "text": f"Location: {label}. Industrial zone. Ideal for development.",
                "level": InsightLevel.SUCCESS
            }]
        elif lu_value in [4, 5, 8]:
            return [{
                "text": f"Location: {label}. Built-up area. Requires specific permits.",
                "level": InsightLevel.WARNING
            }]
        else:
            return []