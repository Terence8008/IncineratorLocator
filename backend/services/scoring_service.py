class ScoringService:
    """Handles policy-based scoring using MCDA approach."""
    
    @staticmethod
    def normalize(value: float, min_val: float, max_val: float, reverse: bool = False) -> float:
        """Normalize value to 0-1 range."""
        if max_val == min_val:
            return 0
        norm = (value - min_val) / (max_val - min_val)
        norm = max(0, min(1, norm))
        return 1 - norm if reverse else norm
    
    def calculate_score(self, features: dict, weights: dict[str, float]) -> float:
        """Calculate weighted policy score."""
        # Calculate individual scores
        s_pop = self.normalize(features["population"], 0, 200, reverse=True)
        s_river = self.normalize(features["dist_river_m"], 0, 1000)
        s_road = self.normalize(features["dist_road_m"], 0, 500, reverse=True)
        s_land = 1.0 if features["land_use"] in [6, 7, 8] else 0.2
        
        # Calculate weighted sum
        total_w = sum(weights.values())
        if total_w == 0:
            return 0
        
        weighted_sum = (
            s_pop * weights['pop'] +
            s_river * weights['river'] +
            s_road * weights['road'] +
            s_land * weights['land']
        )
        
        return round((weighted_sum / total_w) * 100, 1)
