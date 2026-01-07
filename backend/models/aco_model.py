import numpy as np
import json
import networkx as nx
from typing import List, Tuple, Dict, Optional
import os
from math import radians, cos, sin, asin, sqrt


class RoadNetworkGraph:
    """Road network graph representation"""
    
    def __init__(self, geojson_path: str):
        self.graph = nx.Graph()
        self.node_coords = {}  
        self.coord_to_id = {}  
        self.geojson_path = geojson_path
        self.load_road_network()
        
    def load_road_network(self):
            """Load road network from GeoJSON"""
            if not os.path.exists(self.geojson_path):
                raise FileNotFoundError(f"Road network file not found: {self.geojson_path}")
                
            with open(self.geojson_path, encoding='utf-8') as f:  
                geojson_data = json.load(f)
            
            node_id = 0
            
            for feature in geojson_data['features']:
                if feature['geometry']['type'] in ['LineString', 'MultiLineString']:
                    coords = feature['geometry']['coordinates']
                    
                    if feature['geometry']['type'] == 'MultiLineString':
                        coords_list = coords
                    else:
                        coords_list = [coords]
                    
                    for coord_set in coords_list:
                        for i in range(len(coord_set) - 1):
                            start = tuple(coord_set[i][:2])
                            end = tuple(coord_set[i + 1][:2])
                            
                            if start not in self.coord_to_id:
                                self.coord_to_id[start] = node_id
                                self.node_coords[node_id] = start
                                node_id += 1
                            
                            if end not in self.coord_to_id:
                                self.coord_to_id[end] = node_id
                                self.node_coords[node_id] = end
                                node_id += 1
                            
                            start_id = self.coord_to_id[start]
                            end_id = self.coord_to_id[end]
                            
                            distance = self._haversine_distance(start, end)
                            self.graph.add_edge(start_id, end_id, weight=distance)
    
    def _haversine_distance(self, coord1, coord2):
        """Calculate distance between two coordinates in km"""
        lon1, lat1 = radians(coord1[0]), radians(coord1[1])
        lon2, lat2 = radians(coord2[0]), radians(coord2[1])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth radius in km
        return c * r
    
    def find_nearest_node(self, coord: Tuple[float, float]) -> int:
        """Find nearest node to coordinate"""
        min_dist = float('inf')
        nearest_node = None
        
        for node_id, node_coord in self.node_coords.items():
            dist = self._haversine_distance(coord, node_coord)
            if dist < min_dist:
                min_dist = dist
                nearest_node = node_id
        
        return nearest_node
    
    def get_node_coordinate(self, node_id: int) -> Tuple[float, float]:
        """Get coordinate of node"""
        return self.node_coords[node_id]


class ACOPathFinder:
    """Ant Colony Optimization for pathfinding"""
    
    def __init__(self, graph: nx.Graph, node_coords: Dict, 
                 num_ants: int = 25, num_iterations: int = 50,
                 alpha: float = 1.0, beta: float = 3.0, 
                 evaporation_rate: float = 0.5, q: float = 100):
        self.graph = graph
        self.node_coords = node_coords
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.q = q
        
        self.pheromones = {}
        for u, v in self.graph.edges():
            self.pheromones[(u, v)] = 1.0
            self.pheromones[(v, u)] = 1.0
        
        self.best_path = None
        self.best_distance = float('inf')
    
    def _get_neighbors(self, node: int, visited: set) -> List[int]:
        neighbors = list(self.graph.neighbors(node))
        return [n for n in neighbors if n not in visited]
    
    def _calculate_probabilities(self, current: int, neighbors: List[int]) -> np.ndarray:
        if not neighbors:
            return np.array([])
        
        pheromones = np.array([self.pheromones.get((current, n), 0.1) for n in neighbors])
        distances = np.array([self.graph[current][n]['weight'] for n in neighbors])
        heuristics = 1.0 / (distances + 0.001)
        
        probabilities = (pheromones ** self.alpha) * (heuristics ** self.beta)
        total = probabilities.sum()
        
        if total == 0:
            return np.ones(len(neighbors)) / len(neighbors)
        
        return probabilities / total
    
    def _construct_path(self, start: int, end: int) -> Tuple[Optional[List[int]], float]:
        current = start
        path = [current]
        visited = {current}
        total_distance = 0
        
        max_steps = len(self.graph.nodes()) * 2
        steps = 0
        
        while current != end and steps < max_steps:
            neighbors = self._get_neighbors(current, visited)
            
            if not neighbors:
                return None, float('inf')
            
            probabilities = self._calculate_probabilities(current, neighbors)
            next_node = np.random.choice(neighbors, p=probabilities)
            
            path.append(next_node)
            total_distance += self.graph[current][next_node]['weight']
            visited.add(next_node)
            current = next_node
            steps += 1
        
        if current != end:
            return None, float('inf')
        
        return path, total_distance
    
    def _update_pheromones(self, all_paths: List[Tuple[List[int], float]]):
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.evaporation_rate)
        
        for path, distance in all_paths:
            if path and distance < float('inf'):
                pheromone_deposit = self.q / distance
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    self.pheromones[(u, v)] = self.pheromones.get((u, v), 0) + pheromone_deposit
                    self.pheromones[(v, u)] = self.pheromones.get((v, u), 0) + pheromone_deposit
    
    def find_path(self, start: int, end: int) -> Tuple[List[int], float]:
        if not nx.has_path(self.graph, start, end):
            raise ValueError(f"No path exists between nodes")
        
        for iteration in range(self.num_iterations):
            all_paths = []
            
            for ant in range(self.num_ants):
                path, distance = self._construct_path(start, end)
                
                if path:
                    all_paths.append((path, distance))
                    
                    if distance < self.best_distance:
                        self.best_distance = distance
                        self.best_path = path
            
            self._update_pheromones(all_paths)
        
        # If ACO found a path, return it
        if self.best_path is not None:
            print("Path found using ACO")
            return self.best_path, self.best_distance
        
        # Fallback to Dijkstra
        print("ACO failed to find path; falling back to Dijkstra")
        try:
            path = nx.shortest_path(self.graph, start, end, weight='weight')
            distance = nx.shortest_path_length(self.graph, start, end, weight='weight')
            return path, distance
        except nx.NetworkXNoPath:
            return None, float('inf')
    
    def get_path_coordinates(self, path: List[int]) -> List[List[float]]:
        """Convert node IDs to coordinates"""
        return [list(self.node_coords[node]) for node in path]