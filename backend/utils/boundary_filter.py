from pathlib import Path
import geopandas as gpd

# get current script directory
current_dir = Path(__file__).resolve().parent

# go up one folder, then into "data"
json_path = current_dir.parent / "data" / "gadm41_MYS_1.json"

# Load Selangor boundary (Level 1)
gdf = gpd.read_file(json_path)

# Filter only Selangor
selangor = gdf[gdf["NAME_1"] == "Selangor"]

# Save filtered boundary
selangor.to_file("selangor_boundary.geojson", driver="GeoJSON")