import rasterio

# Script for Checking raster tif information
def check_file(filepath):
    print(f"\n--- Checking: {filepath} ---")
    try:
        with rasterio.open(filepath) as src:
            print(f"CRS: {src.crs}")
            print(f"Bounds: {src.bounds}")
            print(f"Width/Height: {src.width}x{src.height}")
            print(f"NoData Value: {src.nodata}")
            # Read a small window to see if data exists
            data = src.read(1)
            print(f"Max Value in Band 1: {data.max()}")
            print(f"Min Value in Band 1: {data.min()}")
    except Exception as e:
        print(f"Error reading file: {e}")

check_file("data/processed/population_selangor.tif")
check_file("data/processed/landuse_selangor.tif")