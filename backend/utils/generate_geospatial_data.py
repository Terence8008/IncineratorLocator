import pandas as pd
import numpy as np
import geopandas as gpd
import random
from pathlib import Path
from shapely.geometry import Point
from sklearn.preprocessing import MinMaxScaler
from utils.feature_extraction import extract_features_from_latlon

DATA_DIR = Path("data/processed")
W_POP, W_RIVER, W_ROAD, W_LAND = 0.35, 0.30, 0.20, 0.15
LANDUSE_SCORES = {1: 0.8, 2: 0.6, 3: 0.2, 4: 0.1, 5: 0.2, 6: 1.0, 7: 0.1, 8: 0.1, 9: 0.5}

def generate_training_data(n_samples=5000):
    boundary = gpd.read_file(DATA_DIR / "selangor_boundary.geojson").dissolve()
    poly = boundary.geometry.values[0]
    minx, miny, maxx, maxy = poly.bounds
    
    data = []
    print(f"Generating {n_samples} points...")
    while len(data) < n_samples:
        lat, lon = random.uniform(miny, maxy), random.uniform(minx, maxx)
        if poly.contains(Point(lon, lat)):
            feat = extract_features_from_latlon(lat, lon)
            # Filter out points with 0 population (usually water/unusable)
            if feat["population"] > 0:
                feat["latitude"], feat["longitude"] = lat, lon
                data.append(feat)

    df = pd.DataFrame(data)

    # Apply MCDA Labeling
    df["landuse_score"] = df["land_use"].map(LANDUSE_SCORES).fillna(0)
    scaler = MinMaxScaler()
    df[["p_n", "ri_n", "ro_n"]] = scaler.fit_transform(df[["population", "dist_river_m", "dist_road_m"]])
    
    df["mcda_score"] = ((1 - df["p_n"]) * W_POP + df["ri_n"] * W_RIVER + 
                        df["ro_n"] * W_ROAD + df["landuse_score"] * W_LAND)
    
    threshold = df["mcda_score"].median()
    df["suitable"] = (df["mcda_score"] >= threshold).astype(int)

    # Save
    cols = ["latitude", "longitude", "population", "land_use", "dist_river_m", "dist_road_m", "suitable"]
    df[cols].to_csv(DATA_DIR / "selangor_training.csv", index=False)
    print("Training data saved.")

if __name__ == "__main__":
    generate_training_data()