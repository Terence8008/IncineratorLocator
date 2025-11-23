import rasterio

for path in ["data/population.tif", "data/landuse.tif"]:
    with rasterio.open(path) as src:
        print(f"File: {path}")
        print("CRS:", src.crs)
        print("Bounds:", src.bounds)
        print("Resolution:", src.res)
        print("Nodata:", src.nodata)
        print("Band count:", src.count)
        print()