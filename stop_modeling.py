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

tag_cols = ['building', 'landuse', 'railway', 'amenity']

features = ox.features_from_place(place, tags)
features = features.to_crs(epsg=3857)

#making all features in point form (for now)
features.geometry = features.geometry.representative_point()

#this returns all features within the 300m distance of a node
#if node has multiple features, there will be row for each feature

features_around_node = gpd.sjoin(
    left_df=gdf_nodes_buffered,
    right_df=features,
    how='left',
    predicate='intersects'
)

#dropping rows where all tag columns nan
features_around_node = features_around_node.dropna(subset=tag_cols, how='all')

#weighting and scoring each tag value pair in a series (row)
def score_agg(series):
    score = bc[series.name]
    if(series['building'] == "apartments"):
        score+=5
    elif(series['building'] == "supermarket"):
        score+=5
    elif(series['landuse'] == "commercial"):
        score+=6
    elif(series['railway'] == "station"):
        score+=9
    elif(series['amenity'] == "hospital"):
        score+=7
    elif(series['amenity'] == "school"):
        score+=7
    elif(series['amenity'] == "university"):
        score+=8
    return score

#calculating score of row based on tags and applying in new column
features_around_node['node_score'] = features_around_node.apply(score_agg, axis=1)

#grouping rows by node id, summing the scores for each id
grouped_score = features_around_node.groupby(level=0)['node_score'].sum()