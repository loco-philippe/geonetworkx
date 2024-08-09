# -*- coding: utf-8 -*-

import shapely
from shapely import LineString, Point
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import networkx as nx
import matplotlib.pyplot as plt

def from_geopandas_edgelist(edge_gdf, source='source', target='target', 
                            edge_attr=None, node_gdf=None, node_id='node_id', node_attr=None):
    '''Returns a GeoGraph from GeoDataFrame containing an edge list.
    
    The GeoDataFrame should contain at least two columns (node id source, node id target).
    An additional GeoDataFrame is used to load nodes.
    The geometry is a shapely object present in a 'geometry' column of each GeoDataFrame.
    If the geometry is present in only one GeoDataFrame, the other geometry is deduced.
    If the geometries are present in both GeoDataFrame, they should be consistent'''
    
    e_gdf = edge_gdf.copy()
    n_gdf = node_gdf.copy() if node_gdf else None
    geom = 'geometry'
    weight = 'weight'
    
    if isinstance(edge_attr, list | tuple):
        edge_attr += [geom, weight]
    elif edge_attr:
        edge_attr = [geom, weight, edge_attr]
        
    if geom in n_gdf and not geom in e_gdf:
        e_gdf = pd.merge(e_gdf, n_gdf.loc[:, (node_id, geom)], how='left', left_on=source, right_on=node_id).rename(columns={geom:'geom_source'})
        e_gdf.pop(node_id) 
        e_gdf = pd.merge(e_gdf, n_gdf.loc[:, (node_id, geom)], how='left', left_on=target, right_on=node_id).rename(columns={geom:'geom_target'})
        e_gdf.pop(node_id) 
        # e_gdfons['geometry'] = pd.Series([LineString([row[3], row[4]]) for row in e_gdf.itertuples()])
        geo_e_gdf = gpd.GeoDataFrame(edge_gdf, geometry = gpd.GeoSeries(e_gdf['geom_source']).shortest_line(gpd.GeoSeries(e_gdf['geom_target'])))
    
    geo_e_gdf[weight] = geo_e_gdf[geom].length
    geo_gr = nx.from_pandas_edgelist(geo_e_gdf, edge_attr=edge_attr)
    
    if n_gdf is not None: 
        dic = n_gdf.to_dict(orient='records')
        nx_dic = {row[node_id]: dict(item for item in row.items() if item[0] != node_id) for row in dic}
        nx.set_node_attributes(geo_gr, nx_dic)
         
    return geo_gr