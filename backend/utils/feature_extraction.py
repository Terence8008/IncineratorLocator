import rasterio
from pathlib import Path
from shapely.geometry import Point
from shapely.ops import unary_union
import geopandas as gpd
import numpy as np

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # backend/utils -> project/
DATA_DIR = PROJECT_ROOT / "data" / "processed"

# Load GeoJSONs
rivers = gpd.read_file(DATA_DIR / "rivers_selangor.geojson")
roads = gpd.read_file(DATA_DIR / "roads_selangor.geojson")


rivers_union = unary_union(rivers.geometry)
roads_union  = unary_union(roads.geometry)

# Open rasters (you can replace with your actual paths)
population_raster = rasterio.open(DATA_DIR/ "population_selangor.tif")
landuse_raster   = rasterio.open( DATA_DIR /"landuse_selangor.tif")


def extract_raster_value(raster, point: Point):
    """Extract raster value at a given Point."""
    coords = [(point.x, point.y)]
    vals = list(raster.sample(coords))
    if vals and vals[0] is not None:
        return vals[0][0]
    else:
        return np.nan

def distance_to_nearest(geom, union_geom):
    """Compute distance from point to nearest feature in unioned geometry."""
    return geom.distance(union_geom)

def extract_features_from_latlon(lat: float, lon: float):
    point = Point(lon, lat)

    population = extract_raster_value(population_raster, point)
    land_use   = extract_raster_value(landuse_raster, point)
    dist_river = distance_to_nearest(point, rivers_union)
    dist_road  = distance_to_nearest(point, roads_union)

    return {
        "population": population,
        "land_use": land_use,
        "dist_river_m": dist_river,
        "dist_road_m": dist_road
    }
