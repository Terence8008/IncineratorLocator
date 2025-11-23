import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from shapely.geometry import Point
from shapely.ops import nearest_points
from rasterio import sample
import random

# === Load Selangor boundary ===
boundary = gpd.read_file("data/selangor_boundary.geojson")
boundary = boundary.dissolve(by="NAME_1")  # Merge into single polygon
polygon = boundary.geometry.values[0]

# === Load rivers and roads, reproject to metric CRS for distance calculation ===
rivers = gpd.read_file("data/rivers_selangor.geojson").to_crs(epsg=3857)
roads = gpd.read_file("data/roads_selangor.geojson").to_crs(epsg=3857)
rivers_union = rivers.geometry.union_all
roads_union = roads.geometry.union_all

# === Function to generate random points inside boundary ===
def generate_random_points(polygon, n_points):
    minx, miny, maxx, maxy = polygon.bounds
    points = []
    while len(points) < n_points:
        random_point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(random_point):
            points.append(random_point)
    return gpd.GeoDataFrame(geometry=points, crs=boundary.crs)

# === Generate 5000 random points ===
print("🎯 Generating 5000 random points within Selangor...")
points_gdf = generate_random_points(polygon, 5000)
print("✅ Points generated.")

# === Function to extract raster values ===
def extract_raster_values(raster_path, points_gdf, column_name):
    with rasterio.open(raster_path) as src:
        values = []
        for point in points_gdf.geometry:
            for val in sample.sample_gen(src, [(point.x, point.y)]):
                values.append(val[0] if val is not None else np.nan)
        points_gdf[column_name] = values
    return points_gdf

# === Extract raster values ===
print("📊 Extracting population values...")
points_gdf = extract_raster_values("data/population_selangor.tif", points_gdf, "population")

print("🌱 Extracting land use values...")
points_gdf = extract_raster_values("data/landuse_selangor.tif", points_gdf, "land_use")

# === Reproject points to metric CRS for distance calculation ===
points_gdf = points_gdf.to_crs(epsg=3857)

print("💧 Cleaning river geometries...")
rivers = gpd.read_file("data/rivers_selangor.geojson").to_crs(epsg=3857)
rivers = rivers[rivers.geometry.notnull()]
rivers = rivers[rivers.is_valid]
rivers = rivers[~rivers.is_empty]
rivers = rivers[rivers.geom_type.isin(["LineString", "MultiLineString"])]
rivers_union = rivers.geometry.unary_union

print("🛣️ Cleaning road geometries...")
roads = gpd.read_file("data/roads_selangor.geojson").to_crs(epsg=3857)
roads = roads[roads.geometry.notnull()]
roads = roads[roads.is_valid]
roads = roads[~roads.is_empty]
roads = roads[roads.geom_type.isin(["LineString", "MultiLineString"])]
roads_union = roads.geometry.unary_union

print("💧 Computing distance to nearest river...")
points_gdf["dist_river_m"] = points_gdf.geometry.apply(
    lambda p: p.distance(nearest_points(p, rivers_union)[1])
)

print("🛣️ Computing distance to nearest main road...")
points_gdf["dist_road_m"] = points_gdf.geometry.apply(
    lambda p: p.distance(nearest_points(p, roads_union)[1])
)

# === Compute distance to rivers and roads ===
print("💧 Computing distance to nearest river...")
points_gdf["dist_river_m"] = points_gdf.geometry.apply(lambda p: p.distance(nearest_points(p, rivers_union)[1]))

print("🛣️ Computing distance to nearest main road...")
points_gdf["dist_road_m"] = points_gdf.geometry.apply(lambda p: p.distance(nearest_points(p, roads_union)[1]))

# === Save final CSV ===
points_gdf["lon"] = points_gdf.to_crs(epsg=4326).geometry.x
points_gdf["lat"] = points_gdf.to_crs(epsg=4326).geometry.y
df = points_gdf.drop(columns="geometry")

df.to_csv("data/selangor_sample_points_features.csv", index=False)
print("✅ Saved: selangor_sample_points_features.csv")