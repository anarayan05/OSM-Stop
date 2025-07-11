import osmnx as ox
import networkx as nx
import pandas as pd
import geopandas as gpd

place = "Emeryville, California, USA"

G = ox.graph.graph_from_place(place, network_type="drive") #downloads street network
gdf_nodes = ox.convert.graph_to_gdfs(G, nodes = True, edges = False)
gdf_nodes = gdf_nodes.to_crs(epsg=3857)
gdf_nodes_buffered = gdf_nodes.copy()
gdf_nodes_buffered['geometry'] = gdf_nodes_buffered.geometry.buffer(300) #300m polygon shape around node

bc = nx.betweenness_centrality(ox.convert.to_digraph(G), weight = "length") #dict: calculates centrality of nodes based on path lengths

#fig, ax = ox.plot.plot_graph(G) to see nodes

existing_stops = ox.features.features_from_place(place, {"highway": "bus_stop"}) #node: dont use this for expirimenting


tags = {
    'building': ['apartments', 'supermarket'],
    'landuse': ['commercial'],
    'railway': ['station'],
    'amenity': ['hospital','school', 'university']
}

#how each tage is weighted
tag_score = {
    'building: apartments': 5,
    'building: supermarket': 5,
    'landuse: commercial': 6,
    'railway: station': 9,
    'amenity: hospital': 7,
    'amenity: school': 7,
    'amenity: university': 8
}

features = ox.features_from_place(place, tags)
features = features.to_crs(epsg=3857)

#this returns all features within the 300m distance of a node
#if node has multiple features, there will be row for each feature

features_around_node = gpd.sjoin(
    left_df=gdf_nodes_buffered,
    right_df=features,
    how='left',
    predicate='intersects'
)

#dropping rows where all columns nan
features_around_node = features_around_node.dropna(axis=1, how="all")
print(features_around_node)


#matching feature keys and values to tags
#to get score

#consider filtering highway nodes

def calculateScore(features, node_id):
    score = bc[node_id] * 4 #initializing with centrality score
    for idx, row in features.iterrows():
        key = row.idx[1] #grabs the type of feature
        value = row.iloc[1] #value of of the type
        if(key in tags.keys()):
            if(value in tags[key]):
                score+=tag_score[key+': '+value]
    return score

node_score_dict = {}       

# for idx, row in gdf_nodes.iterrows():
#     lat = row['y']
#     long = row['x']
#     point = (lat, long)
#     try:
#         nearest_features = ox.features.features_from_point(point, tags, dist=300) #nearest features from tags to each node
#         score = calculateScore(nearest_features, idx)
#         node_score_dict[idx] = score
#         print(f"{point}: {score}")
#     except ox._errors.InsufficientResponseError as e:
#         print("Did not find any features nearby")