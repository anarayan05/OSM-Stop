import osmnx as ox
import pandas as pd

place = "Buffalo, New York, USA"

G = ox.graph.graph_from_place(place, network_type="drive") #downloads street network

#add or delete features later
# rail_station = ox.features.features_from_place(place, {"building": "train_station"}) #polygon
# commercial = ox.features.features_from_place(place, {"landuse": "commercial"}) #polygon

# rail_station_points = rail_station.representative_point() #point
# commercial_points = commercial.representative_point() #point
# existing_stops = ox.features.features_from_place(place, {"highway": "bus_stop"}) #point
# apartments = ox.features.features_from_place(place, {"building": "apartments"}) #point
# hospital = ox.features.features_from_place(place, {"amenity": "hospital"}) #point

tags = {
    'building': ['train_station', 'apartments'],
    'landuse': 'commercial',
    'highway': 'bus_stop',
    'building': 'apartments',
    'amenity': 'hospital'
}

gdf_nodes = ox.convert.graph_to_gdfs(G, nodes = True, edges = False)
gdf_nodes_coord = gdf_nodes.get_coordinates()

point_score_dict = {}

for idx, row in gdf_nodes_coord.iterrows():
    lat = row['y']
    long = row['x']
    point = (lat, long)
    try:
        nearest_features = ox.features.features_from_point(point, tags, dist=300)
        score = 0 #for now
        point_score_dict[point] = score
    except ox._errors.InsufficientResponseError as e:
        print("Did not find any features nearby")


# lat0 = gdf_nodes_coord['y'].iloc[0]
# long0 = gdf_nodes_coord['x'].iloc[0]
# point0 = (lat, long)

# print(point_score_dict[point])

