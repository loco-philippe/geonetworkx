# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 22:40:20 2024

@author: a lab in the Air
"""
from shapely import LineString, Point
import geopandas as gpd
import geonetworkx as gnx 
import networkx as nx 
import pandas as pd


paris = Point(2.3514, 48.8575)
lyon = Point(4.8357, 45.7640)
marseille = Point(5.3691, 43.3026)
bordeaux = Point(-0.56667, 44.833328)

# example 1
simplemap = pd.DataFrame.from_records([
    {'source': 'paris', 'target': 'lyon', 'geometry': LineString([paris, lyon])},
    {'source': 'lyon', 'target': 'marseille', 'geometry': LineString([lyon, marseille])},
    {'source': 'paris', 'target': 'bordeaux', 'geometry': LineString([paris, bordeaux])},
    {'source': 'bordeaux', 'target': 'marseille', 'geometry': LineString([bordeaux, marseille])}    
    ])
geo_simplemap = gpd.GeoDataFrame(simplemap, crs=4326).to_crs(2154)
gr_simplemap = gnx.from_geopandas_edgelist(geo_simplemap)

print(gr_simplemap.to_geopandas_nodelist())

print(nx.shortest_path_length(gr_simplemap, source='paris', target='marseille', weight='weight'))
print(nx.shortest_path(gr_simplemap, source='paris', target='marseille', weight='weight'))

# example 2
simplemap = gpd.GeoDataFrame({'geometry': [LineString([paris, lyon]), LineString([lyon, marseille]), 
    LineString([paris, bordeaux]), LineString([bordeaux, marseille])]}, crs=4326).to_crs(2154)
gr_simplemap = gnx.from_geopandas_edgelist(simplemap)

print(gr_simplemap.to_geopandas_nodelist())

# 0: paris, 1: lyon, 2: bodeaux, 3: marseille
print(nx.shortest_path_length(gr_simplemap, source=0, target=3, weight='weight'))
print(nx.shortest_path(gr_simplemap, source=0, target=3, weight='weight'))