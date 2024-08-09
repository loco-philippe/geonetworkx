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
from geonetworkx.utils import geo_cut, find_edge

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
        attr = attr | {'crs': None}
        super().__init__(incoming_graph_data, **attr)
        
    def insert_node(self, geom, id_node, id_edge, adjust=False):

        edge_att = self.edges[*id_edge]
        list_geo_cut = geo_cut(edge_att['geometry'], geom, adjust=adjust)
        if not list_geo_cut:
            return None
        #print('geo_cut, id_node : ', list_geo_cut, id_node) 
        geo1, geo2, dist = list_geo_cut
        self.add_node(id_node, **{'geometry': geom})
        self.add_edge(id_edge[0], id_node, **(edge_att | {'geometry': geo1}))
        self.add_edge(id_node, id_edge[1], **(edge_att | {'geometry': geo2}))
        self.remove_edge(*id_edge)
        return dist
        
    def to_geopandas_edgelist(self, source='source', target='target', nodelist=None):
        """see `convert.to_geopandas_edgelist`"""
        return to_geopandas_edgelist(self, source=source, target=target, nodelist=nodelist)

    def to_geopandas_nodelist(self, node_id='node_id', nodelist=None): 
        """see `convert.to_geopandas_nodelist`"""
        return to_geopandas_nodelist(self, node_id=node_id, nodelist=nodelist)
    
class GeoGraphError(Exception):
    """GeoGraph Exception"""
