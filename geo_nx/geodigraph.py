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
from geo_nx.utils import geo_cut, cast_id, geo_merge

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
    
