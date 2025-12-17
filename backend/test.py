import geopandas as gpd
from pathlib import Path

# Load your boundary file
DATA_DIR = Path("data")

# Load the full Malaysia file instead
malaysia_json = DATA_DIR / "raw" / "gadm41_MYS_1.json" 
boundary = gpd.read_file(malaysia_json)

# Now these names will actually exist in the file
target_areas = ["Selangor", "W.P. Kuala Lumpur", "W.P. Putrajaya"]
boundary_subset = boundary[boundary['NAME_1'].isin(target_areas)]

# Merge them into one solid mask
combined_boundary = boundary_subset.dissolve()

print(boundary[['NAME_1', 'TYPE_1']])