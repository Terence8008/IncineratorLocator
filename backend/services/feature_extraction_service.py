# services/feature_extraction_service.py
import rasterio
from rasterio.warp import transform
from pathlib import Path
from shapely.geometry import Point
import geopandas as gpd
import numpy as np


class FeatureExtractionService:
    """Handles geospatial feature extraction from coordinates."""
    
    # Coordinate Systems
    WGS84 = "EPSG:4326"
    METRIC_CRS = "EPSG:32648"  # UTM 48N for Selangor
    
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.data_dir = self.project_root / "data" / "processed"
        
        # Cache for loaded resources
        self._rivers_union = None
        self._roads_union = None
        self._pop_raster = None
        self._lu_raster = None
        
        # Load resources on initialization
        self._load_resources()
    
    def _load_resources(self):
        """Load and cache geospatial resources."""
        if self._rivers_union is None:
            rivers = gpd.read_file(self.data_dir / "rivers_selangor.geojson").to_crs(self.METRIC_CRS)
            self._rivers_union = rivers.unary_union
            
            roads = gpd.read_file(self.data_dir / "roads_selangor.geojson").to_crs(self.METRIC_CRS)
            self._roads_union = roads.unary_union
            
            self._pop_raster = rasterio.open(self.data_dir / "population_selangor.tif")
            self._lu_raster = rasterio.open(self.data_dir / "landuse_selangor.tif")
    
    def _transform_coords(self, lon: float, lat: float, target_crs: str) -> tuple:
        """Transform WGS84 coordinates to target CRS."""
        tx, ty = transform(self.WGS84, target_crs, [lon], [lat])
        return tx[0], ty[0]
    
    def _extract_population(self, lon: float, lat: float) -> float:
        """Extract population value from raster."""
        coords = [(lon, lat)]
        pop_sample = list(self._pop_raster.sample(coords))
        pop_val = pop_sample[0][0]
        
        # Handle nodata values
        if np.isclose(pop_val, self._pop_raster.nodata) or pop_val < 0:
            return 0.0
        
        return round(float(pop_val), 2)
    
    def _extract_land_use(self, lon: float, lat: float) -> int:
        """Extract land use category from raster."""
        coords = [(lon, lat)]
        lu_sample = list(self._lu_raster.sample(coords))
        lu_val = lu_sample[0][0]
        
        # Handle nodata values
        if np.isclose(lu_val, self._lu_raster.nodata) or lu_val < 0:
            return 0
        
        return int(lu_val)
    
    def _calculate_distances(self, lon: float, lat: float) -> dict:
        """Calculate distances to rivers and roads in meters."""
        mx, my = self._transform_coords(lon, lat, self.METRIC_CRS)
        point_metric = Point(mx, my)
        
        dist_river = point_metric.distance(self._rivers_union)
        dist_road = point_metric.distance(self._roads_union)
        
        return {
            "dist_river_m": round(float(dist_river), 2),
            "dist_road_m": round(float(dist_road), 2)
        }
    
    def extract_features(self, lat: float, lon: float) -> dict:
        """
        Extract all geospatial features from coordinates.
        
        Args:
            lat: Latitude in WGS84
            lon: Longitude in WGS84
            
        Returns:
            Dictionary containing population, land_use, dist_river_m, dist_road_m
        """
        population = self._extract_population(lon, lat)
        land_use = self._extract_land_use(lon, lat)
        distances = self._calculate_distances(lon, lat)
        
        return {
            "population": population,
            "land_use": land_use,
            **distances
        }
    
    def __del__(self):
        """Clean up raster resources."""
        if self._pop_raster is not None:
            self._pop_raster.close()
        if self._lu_raster is not None:
            self._lu_raster.close()