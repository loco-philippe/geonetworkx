# -*- coding: utf-8 -*-

import shapely
from shapely import LineString, Point
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import geonetworkx as gnx

noeuds = gpd.GeoDataFrame({'node_id': [1, 2, 3], 'city': ['paris', 'lyon', 'marseille'],
                          'geometry': [Point(2.3514, 48.8575), Point(4.8357, 45.7640), Point(5.3691, 43.3026)]}, crs=4326).to_crs(2154)
troncons = gpd.GeoDataFrame({'source':[1, 2], 'target': [2, 3]})
troncons['type'] = 'road'
gr = gnx.from_geopandas_edgelist(troncons, edge_attr=True, node_gdf=noeuds, 2154)