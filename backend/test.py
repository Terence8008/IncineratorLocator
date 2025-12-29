import rasterio
import numpy as np
from pyproj import Transformer

# Path to your processed landuse file
tif_path = "data/processed/landuse_selangor.tif"

# Coordinates for KLCC (roughly center of KL)
lat, lon = 3.1579, 101.7123 

with rasterio.open(tif_path) as src:
    # 1. Transform Lat/Lon to the TIF's internal coordinate system
    # Most TIFs use EPSG:4326, but this handles any CRS mismatch
    transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    
    # 2. Convert coordinates to row/column index
    row, col = src.index(x, y)
    
    # 3. Read the pixel value
    # .read(1) gets the first band
    window = rasterio.windows.Window(col, row, 1, 1)
    value = src.read(1, window=window)
    
    print(f"Metadata CRS: {src.crs}")
    print(f"Pixel value at KLCC (Lat: {lat}, Lon: {lon}): {value[0][0]}")

    # 4. Optional: List all unique values in the whole file
    # This helps see if '8' (Urban) even exists in your dataset
    unique_values = np.unique(src.read(1))
    print(f"Unique values found in this TIF: {unique_values}")