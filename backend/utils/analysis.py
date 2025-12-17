def get_site_insights(features: dict) -> list:
    """
    Analyzes spatial features and returns human-readable insights.
    Levels: 'success' (green), 'warning' (yellow), 'danger' (red)
    """
    insights = []
    
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
    # Assuming 6=Industrial, 1=Agriculture, 5=Residential
    lu = features.get("land_use", 0)
    if lu == 6:
        insights.append({"text": "Land Use: Industrially zoned area. Highly compatible.", "level": "success"})
    elif lu == 5:
        insights.append({"text": "Land Use Conflict: Residential zoning. Significant permit hurdles.", "level": "danger"})
    
    return insights