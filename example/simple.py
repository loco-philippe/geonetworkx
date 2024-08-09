# -*- coding: utf-8 -*-

import shapely
from shapely import LineString, Point
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import geonetworkx as gnx
from geonetworkx import find_edge, geom_to_crs

paris = Point(2.3514, 48.8575)
lyon = Point(4.8357, 45.7640)
marseille = Point(5.3691, 43.3026)
avignon = Point(4.8059, 43.9487)

noeuds = gpd.GeoDataFrame({'node_id': [1, 2, 3], 
                           'city': ['paris', 'lyon', 'marseille'],
                           'geometry': [paris, lyon, marseille]
                           }, crs=4326).to_crs(2154)
troncons = gpd.GeoDataFrame({'source':[1, 2], 'target': [2, 3]})
troncons['type'] = 'road'

gr = gnx.from_geopandas_edgelist(troncons, edge_attr=True, node_gdf=noeuds)

print(gr.to_geopandas_edgelist())
print(gr.to_geopandas_nodelist())

id_edge = find_edge(gr, geom_to_crs(avignon, 4326, 2154), 200000)

print(id_edge)