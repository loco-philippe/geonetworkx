# -*- coding: utf-8 -*-
"""
This module contains the `GeoGraph` class.
"""

import shapely
from shapely import LineString, Point
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import networkx as nx
import matplotlib.pyplot as plt
from geonetworkx.convert import to_geopandas_edgelist
from geonetworkx.convert import to_geopandas_nodelist
from geonetworkx.utils import geo_cut, cast_id

class GeoGraph(nx.Graph):
    """This class analyses geographic graphs.

    *Attributes*

    - **crs** : string or integer - Coordinate Reference System used

    *characteristic (@property)*

    - `iscomplete`
    - `ratecodec`
    - `dmincodec`
    - `dmaxcodec`
    - `rancodec`
    - `typecodec`

    *instance methods*

    - `to_dict`

    """

    def __init__(self, incoming_graph_data=None, **attr):
        """Creation mode :

        *Parameters (multiple attributes)*

        - **idfield** : string or integer - Id of the Field

        *example*

        AnaField is created with a dict
        >>> AnaField(Cfield([1,2,3,3]).to_analysis).to_dict()
        {'lencodec': 4, 'mincodec': 3, 'maxcodec': 4}
        >>> AnaField({'lencodec': 4, 'mincodec': 3, 'maxcodec': 4})
        {'lencodec': 4, 'mincodec': 3, 'maxcodec': 4}

        AnaField is created with parameters
        >>> AnaField(lencodec=4, mincodec=3, maxcodec=4).to_dict()
        {'lencodec': 4, 'mincodec': 3, 'maxcodec': 4}
        >>> AnaField(4, 3, 4).to_dict()
        {'lencodec': 4, 'mincodec': 3, 'maxcodec': 4}
        """
        super().__init__(incoming_graph_data, **attr)
        if 'crs' not in self.graph:
            self.graph['crs'] = None

    def insert_node(self, geom, id_node, id_edge, att_node={}, adjust=False):
    
        att_edge = self.edges[*id_edge]
        new_geo = geo_cut(att_edge['geometry'], geom, adjust=adjust)
        if not new_geo:
            return None
        geo1, geo2, intersect, dist = new_geo
        # print(intersect) 
        self.add_node(id_node, **(att_node | {'geometry': intersect}))
        self.add_edge(id_edge[0], id_node, **(att_edge | {'geometry': geo1, 'weight': geo1.length}))
        self.add_edge(id_node, id_edge[1], **(att_edge | {'geometry': geo2, 'weight': geo2.length}))
        self.remove_edge(*id_edge)
        return dist
        
    def to_geopandas_edgelist(self, source='source', target='target', nodelist=None):
        """see `convert.to_geopandas_edgelist`"""
        return to_geopandas_edgelist(self, source=source, target=target, nodelist=nodelist)

    def to_geopandas_nodelist(self, node_id='node_id', nodelist=None): 
        """see `convert.to_geopandas_nodelist`"""
        return to_geopandas_nodelist(self, node_id=node_id, nodelist=nodelist)

    def plot(self, edges=True, nodes=True, **plotparam):
        plotparam = {'edgecolor': 'black', 'marker': 'o', 
                     'color': 'red', 'markersize': 5} | plotparam
        edgekeys = ['edgecolor']
        nodekeys = ['marker', 'color', 'markersize']
        edgeparam = dict(item for item in plotparam.items() if item[0] in edgekeys)
        nodeparam = dict(item for item in plotparam.items() if item[0] in nodekeys)
        
        fig, ax = plt.subplots()
        if edges: 
            self.to_geopandas_edgelist().plot(ax=ax, **edgeparam)
        if nodes: 
            self.to_geopandas_nodelist().plot(ax=ax, **nodeparam)
        plt.show()

    def explore(self, carte=None, edges=True, nodes=True, **expparam): 
        expparam = {'e_name': 'edges', 'n_name': 'nodes',
                    'e_popup': ['weight'], 'n_popup': None,
                    'e_tooltip': None, 'n_tooltip': None, 
                    'e_color': 'blue', 'n_color': 'red',
                    'n_marker_kwds': {'radius': 5, 'fill': True},
                    'layer': False} | expparam
        edgeparam = dict((k[2:], v) for k, v in expparam.items() if k[:2] == 'e_' and v)
        nodeparam = dict((k[2:], v) for k, v in expparam.items() if k[:2] == 'n_' and v)

        if edges:
            if carte:
                self.to_geopandas_edgelist().explore(m=carte, **edgeparam)
            else:
                carte = self.to_geopandas_edgelist().explore(**edgeparam)
        if nodes:
            if carte:
                self.to_geopandas_nodelist().explore(m=carte, **nodeparam)
            else:
                carte = self.to_geopandas_nodelist().explore(**nodeparam)
        folium.TileLayer("CartoDB positron", show=True).add_to(carte)
        if expparam['layer']:
            folium.LayerControl().add_to(carte)
        return carte

    def find_edge(self, geom, max_distance): 
    
        gdf_pt = gpd.GeoDataFrame({'geometry':[geom.centroid]}, crs=self.graph['crs'])
        gdf_ed = self.to_geopandas_edgelist()
        #print(gdf_ed)
        troncons = gdf_pt.sjoin_nearest(gdf_ed, max_distance=max_distance, distance_col='weight')
        if len(troncons):
            troncon = troncons.sort_values(by='weight').iloc[0]
            
            return [cast_id(troncon['source']), cast_id(troncon['target'])]
        return None

    def find_node(self, geom, max_distance): 
    
        gdf_pt = gpd.GeoDataFrame({'geometry':[geom.centroid]}, crs=self.graph['crs'])
        gdf_no = self.to_geopandas_nodelist()
        #print(gdf_no)
        noeuds = gdf_pt.sjoin_nearest(gdf_no, max_distance=max_distance, distance_col='weight')
        if len(noeuds):
            noeud = noeuds.sort_values(by='weight').iloc[0]
            return cast_id(noeud['node_id'])
        return None
        
class GeoGraphError(Exception):
    """GeoGraph Exception"""
