import numpy as np
import rasterio
import matplotlib.pyplot as plt
from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

# Ensure the router and paths are correctly defined
router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

@router.get("/layers/{layer_name}")
def get_layer_image(layer_name: str):
    # Determine which file to open
    path = DATA_DIR / f"{layer_name}_selangor.tif"
    
    with rasterio.open(path) as src:
        data = src.read(1)
        # Mask out NoData values so they are transparent
        data = np.where(data == src.nodata, np.nan, data)
        
        # Create a plot without axes/borders
        fig = plt.figure(frameon=False)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        
        # Choose color map: 'YlOrRd' for population, 'viridis' for landuse
        cmap = 'YlOrRd' if 'population' in layer_name else 'terrain'
        ax.imshow(data, cmap=cmap, aspect='auto')
        
        output_path = DATA_DIR / f"{layer_name}_temp.png"
        fig.savefig(output_path, transparent=True, dpi=300)
        plt.close(fig)
        
    return FileResponse(output_path)