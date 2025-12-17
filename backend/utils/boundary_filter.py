from pathlib import Path
import geopandas as gpd

# 1. Setup paths
DATA_DIR = Path("data")
json_path = DATA_DIR  / "raw" / "gadm41_MYS_1.json"

# 2. Load the full Malaysia boundary file
gdf = gpd.read_file(json_path)

# 3. Define the areas we need to create a solid Greater Selangor region
# Based on your previous print output: 'KualaLumpur' (no space) and 'Putrajaya'
target_areas = ["Selangor", "KualaLumpur", "Putrajaya"]

# 4. Filter the GeoDataFrame for these three regions
greater_selangor = gdf[gdf["NAME_1"].isin(target_areas)]

# 5. Dissolve them into a single solid polygon 
# This is the crucial step to remove the internal "donut hole" borders
greater_selangor_dissolved = greater_selangor.dissolve()

# 6. Save the new solid boundary
# We use the dissolved version so the clipping tool treats it as one shape
output_path = DATA_DIR / "processed"/"selangor_boundary.geojson"
greater_selangor_dissolved.to_file(output_path, driver="GeoJSON")

print(f"Successfully saved solid boundary to {output_path}")
print(f"Regions included: {greater_selangor['NAME_1'].unique()}")