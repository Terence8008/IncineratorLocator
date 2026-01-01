import geopandas as gpd
import rasterio
from rasterio.mask import mask
from pathlib import Path
import json

# Setup Directory Paths
DATA_DIR = Path("data")
# Use the "full" boundary file you just created
json_path = DATA_DIR / "processed" / "selangor_boundary.geojson"
population_path = DATA_DIR / "raw" / "population.tif"
landuse_path = DATA_DIR / "raw" / "landuse.tif"

# Create output directory
output_dir = DATA_DIR / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

# === Load the pre-processed "Solid" Boundary ===
boundary = gpd.read_file(json_path)

# === Function to clip raster ===
def clip_raster(input_tif, output_tif, boundary_gdf):
    with rasterio.open(input_tif) as src:
        # IMPORTANT: Ensure boundary CRS matches the TIF CRS (e.g., EPSG:4326)
        if boundary_gdf.crs != src.crs:
            boundary_gdf = boundary_gdf.to_crs(src.crs)
        
        # Convert geometry to GeoJSON format for masking
        geoms = [json.loads(boundary_gdf.to_json())["features"][0]["geometry"]]
        
        # Clip the raster
        # all_touched=True ensures small pixels at the edge of KL/Selangor aren't dropped
        out_image, out_transform = mask(src, geoms, crop=True, all_touched=True)
        
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        with rasterio.open(output_tif, "w", **out_meta) as dest:
            dest.write(out_image)

    print(f" Clipped raster saved: {output_tif}")

# === Run the clipping ===
pop_output = output_dir / "population_selangor.tif"
land_output = output_dir / "landuse_selangor.tif"

clip_raster(population_path, pop_output, boundary)
clip_raster(landuse_path, land_output, boundary)