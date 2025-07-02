import osmnx as ox
import pandas as pd

place = "Emeryville, California, USA"

G = ox.graph.graph_from_place(place, network_type="drive") #downloads street network
gdf_nodes = ox.convert.graph_to_gdfs(G, nodes = True, edges = False)
gdf_nodes_coord = gdf_nodes.get_coordinates()

#fig, ax = ox.plot.plot_graph(G) to see nodes

existing_stops = ox.features.features_from_place(place, {"highway": "bus_stop"}) #type; point. dont use this for expirimenting


tags = {
    'building': ['apartments', 'supermarket'],
    'landuse': ['commercial'],
    'railway': ['station'],
    'amenity': ['hospital','school', 'university']
}

#how each tage is weighted
#determine values
tag_score = {
    'building: apartments': 1,
    'building: supermarket': 1,
    'landuse: commercial': 1,
    'railway: station': 1,
    'amenity: hospital': 1,
    'amenity: school': 1,
    'amenity: university': 1
}

#matching feature keys and values to tags
#to get score

#consider adding centrality aspect to calculation (at point)

def calculateScore(features):
    score = 0
    for index, row in features.iterrows():
        key = row.index[1] #grabs the type of feature
        value = row.iloc[1] #value of of the type
        if(key in tags.keys()):
            if(value in tags[key]):
                score+=tag_score[key+': '+value]
    return score
       
point_score_dict = {}       

for idx, row in gdf_nodes_coord.iterrows():
    lat = row['y']
    long = row['x']
    point = (lat, long)
    try:
        nearest_features = ox.features.features_from_point(point, tags, dist=300) #nearest features from tags to each node
        score = calculateScore(nearest_features)
        point_score_dict[point] = score
        print(f"{point}: {score}")
    except ox._errors.InsufficientResponseError as e:
        print("Did not find any features nearby")

