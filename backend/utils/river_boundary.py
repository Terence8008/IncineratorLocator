import geopandas as gpd

rivers = gpd.read_file("data/hotosm_mys_roads_lines_geojson.geojson")
boundary = gpd.read_file("data/selangor_boundary.geojson")
rivers_selangor = gpd.overlay(rivers, boundary, how='intersection')
rivers_selangor.to_file("data/roads_selangor.geojson", driver="GeoJSON")