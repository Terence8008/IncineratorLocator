import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from shapely.geometry import Point
import random
from pathlib import Path
from rasterio.warp import transform
from sklearn.preprocessing import MinMaxScaler

# === Configuration & Paths ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

WGS84 = "EPSG:4326"
METRIC_CRS = "EPSG:32648" 

# --- NEW: Updated MCDA Weights & Scores ---
W_POP = 0.35
W_RIVER = 0.25
W_ROAD = 0.25
W_LAND = 0.15

# Scoring based on your new 9-class system
# 6 (Industrial) is ideal (1.0). 8/9 (Urban) are compatible but complex (0.6).
# 3/4 (Residential) are poor (0.1).
LANDUSE_SCORES = {
    1: 0.7, 2: 0.5, 3: 0.1, 4: 0.1, 5: 0.3,
    6: 1.0, 7: 0.2, 8: 0.6, 9: 0.8
}

# === 1. Load Geospatial Data (Using Full Files) ===
print("Loading 'Full' boundaries and vector data...")
# Use the full boundary we created to include KL/Putrajaya
boundary = gpd.read_file(DATA_DIR / "selangor_boundary.geojson").to_crs(WGS84)
boundary = boundary.dissolve() 
polygon = boundary.geometry.values[0]

rivers = gpd.read_file(DATA_DIR / "rivers_selangor.geojson").to_crs(METRIC_CRS)
roads = gpd.read_file(DATA_DIR / "roads_selangor.geojson").to_crs(METRIC_CRS)
rivers_union = rivers.unary_union
roads_union = roads.unary_union

pop_raster = rasterio.open(DATA_DIR / "population_selangor.tif")
lu_raster = rasterio.open(DATA_DIR / "landuse_selangor.tif")

# === 2. Sampling Logic ===
def generate_random_points(poly, n_points):
    minx, miny, maxx, maxy = poly.bounds
    points = []
    while len(points) < n_points:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            points.append(p)
    return gpd.GeoDataFrame(geometry=points, crs=WGS84)

def get_raster_val(raster, lon, lat):
    tx, ty = transform(WGS84, raster.crs, [lon], [lat])
    for val in raster.sample([(tx[0], ty[0])]):
        return val[0]

N_SAMPLES = 6000 # Increased samples for better KL coverage
print(f"Generating {N_SAMPLES} samples...")
points_gdf = generate_random_points(polygon, N_SAMPLES)

raw_data = []
for geom in points_gdf.geometry:
    lon, lat = geom.x, geom.y
    pop = get_raster_val(pop_raster, lon, lat)
    lu = get_raster_val(lu_raster, lon, lat)
    
    # Check for NoData (using the -3.4e+38 check we found earlier)
    if pop < 0 or lu < 1 or lu > 9 or np.isnan(pop):
        continue

    mx, my = transform(WGS84, METRIC_CRS, [lon], [lat])
    p_metric = Point(mx[0], my[0])
    
    raw_data.append({
        "latitude": lat,
        "longitude": lon,
        "population": pop,
        "land_use": int(lu),
        "dist_river_m": p_metric.distance(rivers_union),
        "dist_road_m": p_metric.distance(roads_union)
    })

df = pd.DataFrame(raw_data)

# === 3. Apply MCDA Logic for Labeling ===
print("Applying refined MCDA scoring...")
df["landuse_score"] = df["land_use"].map(LANDUSE_SCORES).fillna(0)

scaler = MinMaxScaler()
# Normalize distance and population
df[["pop_n", "riv_n", "rod_n"]] = scaler.fit_transform(
    df[["population", "dist_river_m", "dist_road_m"]]
)

# MCDA Calculation:
# (1-pop_n): Lower population is better
# (riv_n): Higher distance from river is better (environmental safety)
# (1-rod_n): Lower distance to road is better (logistics)
df["mcda_score"] = (
    (1 - df["pop_n"]) * W_POP +
    df["riv_n"] * W_RIVER +
    (1 - df["rod_n"]) * W_ROAD +
    df["landuse_score"] * W_LAND
)

# Threshold at 60th percentile for a more "strict" suitability model
threshold = df["mcda_score"].quantile(0.6)
df["suitable"] = (df["mcda_score"] >= threshold).astype(int)

# === 4. Export ===
df_train = df[["latitude", "longitude", "population", "land_use", "dist_river_m", "dist_road_m", "suitable"]]
df_train.to_csv(DATA_DIR / "selangor_training_full.csv", index=False)

print(f"Saved {len(df_train)} records to selangor_training_full.csv")
pop_raster.close()
lu_raster.close()