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
METRIC_CRS = "EPSG:32648"  # UTM 48N for Selangor meters

# MCDA Weights
W_POP = 0.35
W_RIVER = 0.30
W_ROAD = 0.20
W_LAND = 0.15

LANDUSE_SCORES = {
    1: 0.8, 2: 0.6, 3: 0.2, 4: 0.1, 5: 0.2,
    6: 1.0, 7: 0.1, 8: 0.1, 9: 0.5
}

# === 1. Load Geospatial Data ===
print("Loading boundaries and vector data...")
boundary = gpd.read_file(DATA_DIR / "selangor_boundary.geojson").to_crs(WGS84)
boundary = boundary.dissolve() 
polygon = boundary.geometry.values[0]

rivers = gpd.read_file(DATA_DIR / "rivers_selangor.geojson").to_crs(METRIC_CRS)
roads = gpd.read_file(DATA_DIR / "roads_selangor.geojson").to_crs(METRIC_CRS)
rivers_union = rivers.unary_union
roads_union = roads.unary_union

pop_raster = rasterio.open(DATA_DIR / "population_selangor.tif")
lu_raster = rasterio.open(DATA_DIR / "landuse_selangor.tif")

# === 2. Generate Random Points & Extract Features ===
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

N_SAMPLES = 5000
print(f"Generating {N_SAMPLES} samples...")
points_gdf = generate_random_points(polygon, N_SAMPLES)

raw_data = []
for geom in points_gdf.geometry:
    lon, lat = geom.x, geom.y
    pop = get_raster_val(pop_raster, lon, lat)
    lu = get_raster_val(lu_raster, lon, lat)
    
    # Filter NoData and outliers
    if pop == pop_raster.nodata or lu == lu_raster.nodata or pop < 0:
        continue

    # Metric distance
    mx, my = transform(WGS84, METRIC_CRS, [lon], [lat])
    p_metric = Point(mx[0], my[0])
    
    raw_data.append({
        "latitude": lat,
        "longitude": lon,
        "population": pop,
        "land_use": lu,
        "dist_river_m": p_metric.distance(rivers_union),
        "dist_road_m": p_metric.distance(roads_union)
    })

df = pd.DataFrame(raw_data)

# === 3. Apply MCDA Logic for Labeling ===
print("Applying MCDA scoring...")
df["landuse_score"] = df["land_use"].map(LANDUSE_SCORES).fillna(0)

scaler = MinMaxScaler()
df[["pop_n", "riv_n", "rod_n"]] = scaler.fit_transform(
    df[["population", "dist_river_m", "dist_road_m"]]
)

# MCDA Calculation (1 - pop_n because lower population is better)
df["mcda_score"] = (
    (1 - df["pop_n"]) * W_POP +
    df["riv_n"] * W_RIVER +
    df["rod_n"] * W_ROAD +
    df["landuse_score"] * W_LAND
)

# Create Binary Label based on Median
threshold = df["mcda_score"].median()
df["suitable"] = (df["mcda_score"] >= threshold).astype(int)

# === 4. Final Formatting & Export ===
# Arrange columns to match the "Selangor Full" layout for consistency
column_order = [
    "latitude", "longitude", "population", "land_use", 
    "dist_river_m", "dist_road_m", "suitable"
]

df_train = df[column_order]

print(f"Final dataset contains {len(df_train)} valid records.")
df_train.to_csv(DATA_DIR / "selangor_training.csv", index=False)
print("Saved: data/processed/selangor_training.csv")

# Cleanup
pop_raster.close()
lu_raster.close()