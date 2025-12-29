def get_site_insights(features: dict) -> list:
    """
    Analyzes spatial features and returns human-readable insights.
    Levels: 'success' (green), 'warning' (yellow), 'danger' (red)
    """
    insights = []
    lu_value = int(features.get("land_use", 0))

    # Define the mapping based on your TIF values
    LAND_USE_LABELS = {
        1: "Agriculture", 2: "Paddy", 3: "Rural Res",
        4: "Urban Res", 5: "Commercial", 6: "Industrial",
        7: "Roads", 8: "Urban", 9: "City Core"
    }

    label = LAND_USE_LABELS.get(lu_value, "Unknown")
    
    # --- 1. Population Analysis ---
    pop = features.get("population", 0)
    if pop > 80:
        insights.append({"text": "High Population Density: Exceeds safe buffer zone for emissions.", "level": "danger"})
    elif pop > 20:
        insights.append({"text": "Moderate Population: Requires advanced filtration systems.", "level": "warning"})
    else:
        insights.append({"text": "Low Population: Minimal risk to residential areas.", "level": "success"})

    # --- 2. Water Proximity (Environmental Protection) ---
    dist_river = features.get("dist_river_m", 0)
    if dist_river < 500:
        insights.append({"text": "Water Risk: Too close to rivers. High contamination risk.", "level": "danger"})
    elif dist_river < 1000:
        insights.append({"text": "Water Caution: Proximity to water requires strict runoff controls.", "level": "warning"})
    else:
        insights.append({"text": "Water Safety: Sufficient distance from major water bodies.", "level": "success"})

    # --- 3. Logistics (Road Access) ---
    dist_road = features.get("dist_road_m", 0)
    if dist_road > 200:
        insights.append({"text": "Logistics Issue: High cost for waste transport and access.", "level": "danger"})
    else:
        insights.append({"text": "Access Quality: Site is well-connected to the road network.", "level": "success"})

    # --- 4. Land Use Compatibility ---
    lu_value = int(features.get("land_use", 0))
    lu_name = LAND_USE_LABELS.get(lu_value, "Unknown")

    if lu_value == 9:
        insights.append({"text": f"Location: {label}. High-density city center. Strict regulations.", "level": "danger"})
    elif lu_value == 6:
        insights.append({"text": f"Location: {label}. Industrial zone. Ideal for development.", "level": "success"})
    elif lu_value in [4, 5, 8]:
        insights.append({"text": f"Location: {label}. Built-up area. Requires specific permits.", "level": "warning"})
    
    return insights