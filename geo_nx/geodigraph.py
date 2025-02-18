# -*- coding: utf-8 -*-
"""
This module contains the `GeoDiGraph` class.
"""

import geopandas as gpd
import folium
import networkx as nx
import matplotlib.pyplot as plt
from shapely import LineString
from geo_nx.convert import to_geopandas_edgelist, to_geopandas_nodelist
from geo_nx.convert import explore
from geo_nx.utils import geo_cut, cast_id, geo_merge
from geo_nx.algorithms import weight_extend, weight_node_to_graph

GEOM = "geometry"
WEIGHT = "weight"
NODE_ID = "node_id"


class GeoDiGraph(nx.DiGraph):
    """This class analyses geospatial digraphs.

    A geospatial digraph is a digraph where nodes and edges are related to a geometry.

    A GeoDiGraph is a NetworkX DiGraph with a shapely geometry as egde attribute and node attribute.

    The GeoDiGraph 'crs' attribute defines the coordinate reference used.

    *instance methods*

    - `to_geopandas_edgelist`
    - `to_geopandas_nodelist`

    """

    def __init__(self, incoming_graph_data=None, **attr):
        """The initialization of a GeoDiGraph is identical to a DiGraph initialization.
        (with the addition of the creation of a 'crs' attribute - default : None).

        The 'geometry' attribute is mandatory for the GeoDiGraph methods (eg. to_geopandas_edgelist)

        Examples
        --------
        Create an empty graph structure (a "null graph") with no nodes and no edges.

        >>> G = nx.Graph()
        """
        super().__init__(incoming_graph_data, **attr)
        if "crs" not in self.graph:
            self.graph["crs"] = None
            
    def to_geopandas_edgelist(self, source="source", target="target", nodelist=None):
        """see `convert.to_geopandas_edgelist`"""
        return to_geopandas_edgelist(
            self, source=source, target=target, nodelist=nodelist
        )

    def to_geopandas_nodelist(self, node_id="node_id", nodelist=None):
        """see `convert.to_geopandas_nodelist`"""
        return to_geopandas_nodelist(self, node_id=node_id, nodelist=nodelist)
    
    def explore(
        self,
        refmap: dict|folium.Map =None,
        edges=True,
        nodes=True,
        nodelist: list|None =None,
        layercontrol=False,
        **param,
    ) -> folium.Map:
        """see `convert.explore`"""
        return explore(self, refmap=refmap, edges=edges, nodes=nodes, 
                       nodelist=nodelist, layercontrol=layercontrol, **param) 

    def weight_extend(self, edge, ext_gr, radius=None, n_attribute=None, n_active=None):
        """see `algorithms.weight_extend`"""
        return weight_extend(self, edge, ext_gr, radius=radius, 
                             n_attribute=n_attribute, n_active=n_active)    
    
    def weight_node_to_graph(
        graph, node, ext_gr, radius=None, attribute=None, active=None):
        """see `algorithms.weight_node_to_graph`"""
        return weight_node_to_graph(graph, node, ext_gr, radius=radius, 
                                    attribute=attribute, active=active)
    