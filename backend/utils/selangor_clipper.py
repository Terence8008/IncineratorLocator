import geopandas as gpd
import rasterio
from rasterio.mask import mask
from pathlib import Path
import json

# Code for processing raw population and landuse datat to malaysia

DATA_DIR = Path("data")

# go up one folder, then into "data"
json_path = DATA_DIR / "processed" / "selangor_boundary.geojson"
population_path = DATA_DIR / "raw" / "population.tif"
landuse_path = DATA_DIR / "raw" / "landuse.tif"

# === Load Selangor boundary ===
boundary = gpd.read_file(json_path)

# Filter for Selangor AND the Federal Territories (KL and Putrajaya)
# Note: Check your GeoJSON 'NAME_1' values; they are usually 'Selangor', 
# 'Kuala Lumpur', and 'Putrajaya'
target_areas = ["Selangor", "Kuala Lumpur", "Putrajaya"]
boundary = boundary[boundary['NAME_1'].isin(target_areas)]

# GADM sometimes includes multiple polygons; dissolve into one
boundary = boundary.dissolve(by="NAME_1")

# Convert boundary geometry to GeoJSON format for rasterio
geojson_geom = [json.loads(boundary.to_json())["features"][0]["geometry"]]

# === Function to clip raster ===
def clip_raster(input_tif, output_tif, geometry):
    with rasterio.open(input_tif) as src:
        out_image, out_transform = mask(src, geometry, crop=True)
        out_meta = src.meta.copy()

        # Update metadata
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        with rasterio.open(output_tif, "w", **out_meta) as dest:
            dest.write(out_image)

    print(f" Clipped raster saved: {output_tif}")

# === Clip both layers ===
clip_raster(population_path, "population_selangor.tif", geojson_geom)
clip_raster(landuse_path, "landuse_selangor.tif", geojson_geom)