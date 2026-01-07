from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.layer_service import LayerService

router = APIRouter()

# Initialize service
layer_service = LayerService()


@router.get("/layers/{layer_name}")
def get_layer_image(layer_name: str):
    """
    Generate and return a static visualization of a geospatial layer.
    
    Args:
        layer_name: Name of the layer (e.g., 'population', 'landuse', 'rivers')
    
    Returns:
        PNG image of the layer visualization
    """
    try:
        image_path = layer_service.generate_layer_image(layer_name)
        return FileResponse(image_path, media_type="image/png")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating layer image: {str(e)}")

@router.get("/layers", response_model=dict)
def list_available_layers():
    """
    List all available geospatial layers.
    
    Returns:
        Dictionary of available layers with their metadata
    """
    layers = layer_service.get_available_layers()
    return {"layers": layers}