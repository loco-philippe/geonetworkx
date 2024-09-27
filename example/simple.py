# -*- coding: utf-8 -*-

from shapely import LineString, Point
import numpy as np
import geopandas as gpd
import geo_nx as gnx
from geo_nx import geom_to_crs

paris = Point(2.3514, 48.8575)
lyon = Point(4.8357, 45.7640)
marseille = Point(5.3691, 43.3026)
avignon = Point(4.8059, 43.9487)
bordeaux = Point(-0.56667, 44.833328)
toulouse = Point(1.43333, 43.599998)

nd = np.array([[1, 'paris', paris],
               [2, 'lyon', lyon],
               [3, 'marseille', marseille],
               [4, 'bordeaux', bordeaux],
               [5, 'toulouse', toulouse]])
noeuds = gpd.GeoDataFrame({'node_id': nd[:, 0], 'city': nd[:, 1], 'geometry': nd[:, 2], 'type': 'noeud'}, 
                          crs=4326).to_crs(2154)

tr = np.array([[1, 2], [2, 3], [1, 4], [4, 5]])
troncons = gpd.GeoDataFrame({'source': tr[:, 0], 'target': tr[:, 1]})
troncons['type'] = 'road'

gr = gnx.from_geopandas_edgelist(troncons, edge_attr=True, node_gdf=noeuds)

print(gr.to_geopandas_edgelist())
print(gr.to_geopandas_nodelist())
gr.plot(edgecolor='blue', markersize=20)
param_exp = {'e_tooltip': "type", 'e_popup': ['type', 'weight', 'source', 'target'], 
             'e_name': 'troncons', 'n_tooltip': "city", 'n_popup': ['city', 'node_id']}
carte = gr.explore(**param_exp)
carte.save('test.html')

avi_2154 = geom_to_crs(avignon, 4326, 2154)
id_edge = gr.find_edge(avi_2154, 200000)
if id_edge:
    dist = gr.insert_node(avi_2154, max(gr.nodes)+1, id_edge, 
                          att_node={'city': 'avignon'}, adjust=True)
    print('dist : ', dist)
carte = gr.explore(**param_exp)
carte.save('test2.html')
print(gr.to_geopandas_edgelist())
print(gr.to_geopandas_nodelist())

stat1 = Point(844000, 6318000)
dis1 = stat1.distance(avi_2154)
geo1 = LineString([avi_2154, stat1])
gr.add_node('st01', **{'geometry': stat1, 'type': 'irve'})
gr.nodes[6]['type'] = 'station'
gr.add_edge(6, 'st01', **{'geometry':geo1, 'weight': dis1, 'type': 'st_irve'})
carte = gr.explore(**param_exp)
carte.save('test2.html')
print(gr.to_geopandas_edgelist())
print(gr.to_geopandas_nodelist())

