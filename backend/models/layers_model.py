# models/layer_models.py
from pydantic import BaseModel
from typing import List, Optional


class LayerInfo(BaseModel):
    """Information about an available layer."""
    name: str
    display_name: str
    description: str
    type: str  # 'raster' or 'vector'


class AvailableLayersResponse(BaseModel):
    """Response containing all available layers."""
    layers: List[LayerInfo]