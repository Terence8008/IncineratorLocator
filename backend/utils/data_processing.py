# app/data_processing.py

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Weight constants (reuse for API also)
W_POP = 0.35
W_RIVER = 0.30
W_ROAD = 0.20
W_LAND = 0.15

LANDUSE_SCORES = {
    1: 0.8,
    2: 0.6,
    3: 0.2,
    4: 0.1,
    5: 0.2,
    6: 1.0,
    7: 0.1,
    8: 0.1,
    9: 0.5
}

def compute_mcda(df):
    """Compute MCDA suitability score for DataFrame with population, land_use, dist_river_m, dist_road_m."""

    # Land use suitability
    df["landuse_score"] = df["land_use"].map(LANDUSE_SCORES)

    # Continuous feature normalization
    scaler = MinMaxScaler()
    df[["population_norm", "dist_river_norm", "dist_road_norm"]] = scaler.fit_transform(
        df[["population", "dist_river_m", "dist_road_m"]]
    )

    # Invert population (low pop = good)
    df["population_norm"] = 1 - df["population_norm"]

    # MCDA weighted scoring
    df["mcda_score"] = (
        W_POP  * df["population_norm"] +
        W_RIVER * df["dist_river_norm"] +
        W_ROAD * df["dist_road_norm"] +
        W_LAND * df["landuse_score"]
    )

    # Threshold → binary suitability
    threshold = df["mcda_score"].median()
    df["suitable"] = (df["mcda_score"] >= threshold).astype(int)

    return df
