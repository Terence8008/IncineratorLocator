from models.aco_model import RoadNetworkGraph, ACOPathFinder
from typing import Dict, Tuple
from pathlib import Path
import os
import csv


class RouteService:
    """Service for route optimization operations"""
    
    def __init__(self):
        """
        Initialize route service
        
        Args:
            road_geojson_path: Path to road network GeoJSON
            landfill_csv_path: Path to CSV file with landfill data
            aco_config: ACO algorithm parameters
        """
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.aco_config = {
            'num_ants': 25,
            'num_iterations': 100,
            'alpha': 1.0,
            'beta': 3.0,
            'evaporation_rate': 0.5,
            'q': 100
        }

        self.road_network = None
        self.landfills = []
        
        # Load landfills from CSV
        self._load_landfills_from_csv(self.project_root/ "data" / "processed"/ "selangor_landfills.csv")
        
        # Initialize road network
        try:
            self.road_network = RoadNetworkGraph(self.project_root/ "data" / "processed"/ "roads_selangor.geojson")
            print(" Route service initialized successfully")
        except Exception as e:
            print(f" Failed to initialize route service: {str(e)}")
            raise
    
    def _load_landfills_from_csv(self, csv_path: str):
        """
        Load landfill data from CSV file
        
        Expected CSV format:
        Name,Latitude,Longitude,Notes
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Landfill CSV file not found: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    landfill = {
                        'name': row['Name'].strip(),
                        'latitude': float(row['Latitude']),
                        'longitude': float(row['Longitude']),
                        'notes': row.get('Notes', '').strip()
                    }
                    self.landfills.append(landfill)
                except (ValueError, KeyError) as e:
                    print(f"⚠ Warning: Skipping invalid row in CSV: {row}. Error: {e}")
        
        print(f" Loaded {len(self.landfills)} landfills from CSV")
        
        if len(self.landfills) == 0:
            raise ValueError("No valid landfill data found in CSV file")
    
    def find_nearest_landfill(self, incinerator_coord: Tuple[float, float]) -> Tuple[Dict, float]:
        """
        Find nearest landfill to incinerator location
        
        Args:
            incinerator_coord: (lon, lat) tuple
            
        Returns:
            (nearest_landfill_dict, straight_line_distance)
        """
        min_dist = float('inf')
        nearest_landfill = None
        
        for landfill in self.landfills:
            landfill_coord = (landfill['longitude'], landfill['latitude'])
            dist = self.road_network._haversine_distance(incinerator_coord, landfill_coord)
            if dist < min_dist:
                min_dist = dist
                nearest_landfill = landfill
        
        return nearest_landfill, min_dist
    
    def optimize_route(self, latitude: float, longitude: float) -> Dict:
        """
        Optimize route from incinerator to nearest landfill
        
        Args:
            latitude: Latitude of incinerator
            longitude: Longitude of incinerator
            
        Returns:
            Dictionary with route optimization results
        """
        incinerator_coord = (longitude, latitude)  # Convert to (lon, lat)
        
        # Find nearest landfill
        nearest_landfill, straight_dist = self.find_nearest_landfill(incinerator_coord)
        landfill_index = self.landfills.index(nearest_landfill)
        landfill_coord = (nearest_landfill['longitude'], nearest_landfill['latitude'])
        
        print(f" Nearest landfill: {nearest_landfill['name']} ({straight_dist:.2f} km)")
        
        # Map to road network nodes
        start_node = self.road_network.find_nearest_node(incinerator_coord)
        end_node = self.road_network.find_nearest_node(landfill_coord)
        print(f" Mapped to road nodes: {start_node} -> {end_node}")
        
        # Run ACO
        aco = ACOPathFinder(
            self.road_network.graph,
            self.road_network.node_coords,
            **self.aco_config
        )
        
        path, distance = aco.find_path(start_node, end_node)
        print(f"ACO find_path result: path={path}, distance={distance}")
        path_coords = aco.get_path_coordinates(path)
        
        return {
            'incinerator_location': list(incinerator_coord),
            'landfill_name': nearest_landfill['name'],
            'landfill_location': list(landfill_coord),
            'landfill_notes': nearest_landfill['notes'],
            'landfill_index': landfill_index,
            'straight_line_distance_km': straight_dist,
            'road_distance_km': distance,
            'path_coordinates': path_coords,
            'num_waypoints': len(path),
            'distance_ratio': distance / straight_dist if straight_dist > 0 else 1.0
        }
