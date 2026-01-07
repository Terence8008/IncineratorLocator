# services/layer_service.py
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from pathlib import Path
from typing import List


class LayerService:
    """Handles geospatial layer visualization and image generation."""
    
    # Color palettes for different layer types
    PLANNING_PALETTE = [
        "#a6d854",  # 1: Non-paddy Agriculture (Light Green)
        "#8da0cb",  # 2: Paddy Fields (Soft Blue)
        "#e78ac3",  # 3: Rural Residential (Pink)
        "#ffd92f",  # 4: Urban Residential (Yellow)
        "#fc8d62",  # 5: Commercial/Institutional (Orange)
        "#66c2a5",  # 6: Industrial/Infrastructure (Teal)
        "#808080",  # 7: Roads (Grey)
        "#e41a1c",  # 8: Urban (Red)
        "#7f0000"   # 9: City Core/KL (Dark Red/Maroon)
    ]
    
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.data_dir = self.project_root / "data" / "processed"
        self.output_dir = self.data_dir / "temp_images"
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_layer_image(self, layer_name: str) -> Path:
        """
        Generate a PNG visualization of a geospatial layer.
        
        Args:
            layer_name: Name of the layer to visualize
            
        Returns:
            Path to the generated PNG image
            
        Raises:
            FileNotFoundError: If the layer file doesn't exist
        """
        raster_path = self.data_dir / f"{layer_name}_selangor.tif"
        
        if not raster_path.exists():
            raise FileNotFoundError(f"Layer '{layer_name}' not found")
        
        # Read and process raster data
        data = self._read_raster(raster_path)
        
        # Generate visualization
        fig, ax = self._create_figure()
        
        if 'population' in layer_name:
            self._render_population_layer(ax, data)
        else:
            self._render_landuse_layer(ax, data)
        
        # Save and return
        output_path = self.output_dir / f"{layer_name}_temp.png"
        self._save_figure(fig, output_path)
        
        return output_path
    
    def _read_raster(self, path: Path) -> np.ndarray:
        """Read raster data and handle nodata values."""
        with rasterio.open(path) as src:
            data = src.read(1).astype(float)
            data[data == src.nodata] = np.nan
        return data
    
    def _create_figure(self) -> tuple:
        """Create a matplotlib figure with no frame or axes."""
        fig = plt.figure(frameon=False, figsize=(10, 10))
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        return fig, ax
    
    def _render_population_layer(self, ax, data: np.ndarray):
        """Render population density layer."""
        ax.imshow(data, cmap='YlOrRd', aspect='auto')
    
    def _render_landuse_layer(self, ax, data: np.ndarray):
        """Render land use planning layer with custom colors."""
        custom_cmap = ListedColormap(self.PLANNING_PALETTE)
        ax.imshow(data, cmap=custom_cmap, aspect='auto', vmin=1, vmax=9)
    
    def _save_figure(self, fig, output_path: Path):
        """Save figure to file and close."""
        fig.savefig(output_path, transparent=True, dpi=300)
        plt.close(fig)
    
    def cleanup_old_images(self, max_age_hours: int = 24):
        """
        Clean up old temporary images.
        
        Args:
            max_age_hours: Delete images older than this many hours
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for image_file in self.output_dir.glob("*_temp.png"):
            file_age = current_time - image_file.stat().st_mtime
            if file_age > max_age_seconds:
                image_file.unlink()

    def get_available_layers(self) -> List[dict]:
        """Get list of all available layers."""
        available_layers = []
        
        for tif_file in self.data_dir.glob("*_selangor.tif"):
            layer_name = tif_file.stem.replace("_selangor", "")
            
            # Determine display info based on layer name
            if "population" in layer_name:
                display_name = "Population Density"
                description = "Population density distribution across Selangor"
                layer_type = "raster"
            elif "landuse" in layer_name:
                display_name = "Land Use Planning"
                description = "Land use categories and zoning information"
                layer_type = "raster"
            else:
                display_name = layer_name.replace("_", " ").title()
                description = f"{display_name} layer"
                layer_type = "raster"
            
            available_layers.append({
                "name": layer_name,
                "display_name": display_name,
                "description": description,
                "type": layer_type
            })
        
        return available_layers