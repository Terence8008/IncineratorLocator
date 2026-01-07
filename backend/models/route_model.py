from pydantic import BaseModel, Field, validator
from typing import List, Tuple, Optional


class RouteRequest(BaseModel):
    """Request model for route optimization"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of incinerator location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of incinerator location")
    


class NearestLandfill(BaseModel):
    """Nearest landfill information"""
    name: str
    index: int
    coordinates: List[float]
    straight_line_distance_km: float


class OptimizedRoute(BaseModel):
    """Optimized route information"""
    road_distance_km: float
    distance_ratio: float
    num_waypoints: int
    path_coordinates: List[List[float]]


class RouteResponse(BaseModel):
    """Response model for route optimization"""
    success: bool
    incinerator_location: List[float]
    nearest_landfill: NearestLandfill
    optimized_route: OptimizedRoute