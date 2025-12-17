import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Prepare sample point for training

df = pd.read_csv("data/processed/selangor_sample_points_features.csv")

# Weight constants
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
    9: 0.5,
}


# 1. Land use scores
df["landuse_score"] = df["land_use"].map(LANDUSE_SCORES)

# 2. Normalize continuous values
scaler = MinMaxScaler()
df[["population_norm", "dist_river_norm", "dist_road_norm"]] = scaler.fit_transform(
    df[["population", "dist_river_m", "dist_road_m"]]
)

df["population_norm"] = 1 - df["population_norm"]  # lower pop = better

# 3. MCDA weighted score
df["mcda_score"] = (
    df["population_norm"] * W_POP +
    df["dist_river_norm"] * W_RIVER +
    df["dist_road_norm"] * W_ROAD +
    df["landuse_score"] * W_LAND
)

# 4. Binary label
threshold = df["mcda_score"].median()
df["suitable"] = (df["mcda_score"] >= threshold).astype(int)

df_full = df[[
    "population",
    "land_use",
    "dist_river_m",
    "dist_road_m",
    "mcda_score",
    "lon",
    "lat",
    "suitable"
]]
df_full.to_csv("data/processed/selangor_full.csv", index=False)


# OUTPUT B: ML Training CSV (no mcda_score)
df_train = df[[
    "population",
    "land_use",
    "dist_river_m",
    "dist_road_m",
    "lon",
    "lat",
    "suitable"
]]
df_train.to_csv("data/processed/selangor_training.csv", index=False)
