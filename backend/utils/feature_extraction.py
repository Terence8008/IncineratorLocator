import rasterio
from rasterio.warp import transform
from pathlib import Path
from shapely.geometry import Point
import geopandas as gpd
import numpy as np

# Functions to assist extracting features from a coordinates

# Setup paths relative to this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

# Coordinate Systems
WGS84 = "EPSG:4326"
METRIC_CRS = "EPSG:32648"  # UTM 48N for Selangor

# Global variables to cache loaded data (prevents reloading on every API call)
_rivers_union = None
_roads_union = None
_pop_raster = None
_lu_raster = None

def _load_resources():
    global _rivers_union, _roads_union, _pop_raster, _lu_raster
    if _rivers_union is None:
        rivers = gpd.read_file(DATA_DIR / "rivers_selangor.geojson").to_crs(METRIC_CRS)
        _rivers_union = rivers.unary_union
        
        roads = gpd.read_file(DATA_DIR / "roads_selangor.geojson").to_crs(METRIC_CRS)
        _roads_union = roads.unary_union
        
        _pop_raster = rasterio.open(DATA_DIR / "population_selangor.tif")
        _lu_raster = rasterio.open(DATA_DIR / "landuse_selangor.tif")

def get_transformed_coords(lon, lat, target_crs):
    """Transforms WGS84 coordinates to a target CRS."""
    tx, ty = transform(WGS84, target_crs, [lon], [lat])
    return tx[0], ty[0]

import numpy as np

def extract_features_from_latlon(lat: float, lon: float):
    _load_resources()
    
    # 1. Prepare coordinates
    coords = [(lon, lat)]

    # 2. Extract Population
    pop_sample = list(_pop_raster.sample(coords))
    pop_val = pop_sample[0][0]
    
    # Critical: Use np.isclose or check against the actual .nodata property
    if np.isclose(pop_val, _pop_raster.nodata) or pop_val < 0:
        pop_val = 0.0

    # 3. Extract Land Use
    lu_sample = list(_lu_raster.sample(coords))
    lu_val = lu_sample[0][0]
    
    if np.isclose(lu_val, _lu_raster.nodata) or lu_val < 0:
        lu_val = 0
    else:
        lu_val = int(lu_val) # Land use is a category code

    # 4. Metric Distances (Stay with UTM 48N for meters)
    mx, my = transform("EPSG:4326", "EPSG:32648", [lon], [lat])
    p_metric = Point(mx[0], my[0])
    
    dist_river = p_metric.distance(_rivers_union)
    dist_road = p_metric.distance(_roads_union)

    return {
        "population": round(float(pop_val), 2),
        "land_use": int(lu_val),
        "dist_river_m": round(float(dist_river), 2),
        "dist_road_m": round(float(dist_road), 2)
    }