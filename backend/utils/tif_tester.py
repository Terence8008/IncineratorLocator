import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np

# Path to your tif file
file_path = "C:/Users/Terence/Desktop/Terence/Apu/Sem 6/FYP/Project/data/raw/landuse.tif"

with rasterio.open(file_path) as src:
    # 1. Print Metadata to check if coordinates are correct
    print(f"Bands: {src.count}")
    print(f"Width/Height: {src.width}x{src.height}")
    print(f"CRS: {src.crs}")  # Should be EPSG:4326 for Lat/Lon
    print(f"Bounds: {src.bounds}") 
    
    # 2. Read the data
    # Band 1 is usually the data layer
    data = src.read(1)
    
    # 3. Handle 'NoData' values for better visualization
    # Replace nodata values with NaN so they don't skew the colorbar
    data = data.astype('float32')
    data[data == src.nodata] = np.nan

    # 4. Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Use show() to keep geographic coordinates on the axes
    img = show(src, ax=ax, cmap='viridis', title="Raw TIF Visualization")
    
    # Add a colorbar
    im = ax.get_images()[0]
    fig.colorbar(im, ax=ax, label='Value')
    
    plt.show()

    # 5. Diagnostic Check: Is it all zeros?
    if np.nanmax(data) == np.nanmin(data):
        print("Warning: The file contains only one value (possibly all 0 or empty).")
    else:
        print(f"Data Range: {np.nanmin(data)} to {np.nanmax(data)}")