from fastapi import APIRouter, Query, HTTPException
from services.route_service import RouteService
from models.route_model import (
    RouteResponse, 
    NearestLandfill,
    OptimizedRoute
)

router = APIRouter()

route_service = RouteService()

@router.get("/check-route-to-landfill", response_model=RouteResponse)
def check_route_to_landfill(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude of incinerator location"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude of incinerator location")
):
    """
    Optimize route from incinerator to nearest landfill using ACO algorithm.
    
    Finds the nearest landfill and calculates the optimal road route
    considering the actual road network topology.
    """
    
    if route_service is None:
        raise HTTPException(status_code=500, detail="Route service not initialized")
    
    try:
        print(f"\n{'='*60}")
        print(f"Route optimization request: ({latitude}, {longitude})")
        
        # Delegate to service
        result = route_service.optimize_route(latitude, longitude)
        
        print(f" Route optimized: {result['road_distance_km']:.2f} km")
        print(f"{'='*60}\n")
        
        # Build response
        return RouteResponse(
            success=True,
            incinerator_location=result['incinerator_location'],
            nearest_landfill=NearestLandfill(
                name=result['landfill_name'],
                index=result['landfill_index'],
                coordinates=result['landfill_location'],
                straight_line_distance_km=round(result['straight_line_distance_km'], 2)
            ),
            optimized_route=OptimizedRoute(
                road_distance_km=round(result['road_distance_km'], 2),
                distance_ratio=round(result['distance_ratio'], 2),
                num_waypoints=result['num_waypoints'],
                path_coordinates=result['path_coordinates']
            )
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f" Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Route optimization failed: {str(e)}")
