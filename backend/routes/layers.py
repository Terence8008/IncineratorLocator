import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

# Ensure the router and paths are correctly defined
router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

@router.get("/layers/{layer_name}")
def get_layer_image(layer_name: str):
    path = DATA_DIR / f"{layer_name}_selangor.tif"
    
    with rasterio.open(path) as src:
        data = src.read(1).astype(float)
        data[data == src.nodata] = np.nan
        
        fig = plt.figure(frameon=False, figsize=(10, 10))
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        
        if 'population' in layer_name:
            cmap = 'YlOrRd'
            # Population usually varies widely, so auto-scale is okay here
            ax.imshow(data, cmap=cmap, aspect='auto')
        else:
            # Define a custom palette: 
            # KL (9) is now Dark Red, Residential (4) is Yellow, etc.
            planning_palette = [
                "#a6d854", # 1: Non-paddy Agriculture (Light Green)
                "#8da0cb", # 2: Paddy Fields (Soft Blue)
                "#e78ac3", # 3: Rural Residential (Pink)
                "#ffd92f", # 4: Urban Residential (Yellow)
                "#fc8d62", # 5: Commercial/Institutional (Orange)
                "#66c2a5", # 6: Industrial/Infrastructure (Teal)
                "#808080", # 7: Roads (Grey)
                "#e41a1c", # 8: Urban (Red)
                "#7f0000"  # 9: City Core/KL (Dark Red/Maroon) - NO LONGER WHITE
            ]
            custom_cmap = ListedColormap(planning_palette)
            ax.imshow(data, cmap=custom_cmap, aspect='auto', vmin=1, vmax=9)

        output_path = DATA_DIR / f"{layer_name}_temp.png"
        fig.savefig(output_path, transparent=True, dpi=300)
        plt.close(fig)
        
    return FileResponse(output_path)    