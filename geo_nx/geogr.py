# -*- coding: utf-8 -*-
"""
This module contains the `GeoGraph` class.
"""
from abc import ABC
import geo_nx as gnx
import geopandas as gpd
import folium
import networkx as nx
import matplotlib.pyplot as plt
from shapely import LineString
from geo_nx.convert import to_geopandas_edgelist, to_geopandas_nodelist
from geo_nx.convert import explore, plot
from geo_nx.utils import geo_cut, cast_id, geo_merge
from geo_nx.algorithms import weight_extend, weight_node_to_graph

GEOM = "geometry"
WEIGHT = "weight"
NODE_ID = "node_id"


class GeoGr(ABC):
    """This class analyses geospatial graphs.

    A geospatial graph is a graph where nodes and edges are related to a geometry.

    A GeoGraph is a NetworkX Graph with a shapely geometry as egde attribute and node attribute.

    The GeoGraph 'crs' attribute defines the coordinate reference used.

    *instance methods*

    - `to_geopandas_edgelist`
    - `to_geopandas_nodelist`
    - `plot`
    - `explore`
    - `weight_extend`
    - `clean_attributes`
    - `remove_attributes`
    - `weight_node_to_graph`
    - `weight_extend`

    """
    def explore(
        self,
        refmap: dict|folium.Map =None,
        edges: bool=True,
        nodes: bool=True,
        nodelist: list|None =None,
        layercontrol=False,
        **param,
    ) -> folium.Map:
        """see `convert.explore`"""
        return explore(self, refmap=refmap, edges=edges, nodes=nodes, 
                       nodelist=nodelist, layercontrol=layercontrol, **param) 
    
    def plot(self, edges: bool=True, nodes: bool=True, **param):
        """see `convert.plot`"""
        return plot(self, edges=edges, nodes=nodes, **param)
    
    def to_geopandas_edgelist(self, source="source", target="target", nodelist=None):
        """see `convert.to_geopandas_edgelist`"""
        return to_geopandas_edgelist(
            self, source=source, target=target, nodelist=nodelist
        )

    def to_geopandas_nodelist(self, node_id="node_id", nodelist=None):
        """see `convert.to_geopandas_nodelist`"""
        return to_geopandas_nodelist(self, node_id=node_id, nodelist=nodelist)
    
    def weight_extend(self, edge, ext_gr, radius=None, n_attribute=None, n_active=None, gr_rev=None):
        """see `algorithms.weight_extend`"""
        return weight_extend(self, edge, ext_gr, radius=radius, 
                             n_attribute=n_attribute, n_active=n_active, gr_rev=gr_rev)    
    
    def weight_node_to_graph(
        graph, node, ext_gr, is_source, radius=None, attribute=None, active=None, gr_rev=None):
        """see `algorithms.weight_node_to_graph`"""
        return weight_node_to_graph(graph, node, ext_gr, is_source, radius=radius, 
                                    attribute=attribute, active=active, gr_rev=gr_rev)

    def clean_attributes(self, nodes=True, edges=True):
        """remove attributes with None value

        Parameters
        ----------
        nodes : boolean (default True)
            Remove None attribute if True.
        edges : boolean (default True)
            Remove None attribute if True.

        Returns
        -------
        None
        """
        if nodes:
            for node in self:
                l_attr = list(self.nodes[node])
                for attr in l_attr:
                    if not self.nodes[node][attr]:
                        del self.nodes[node][attr]
        if edges:
            for edge in self.edges:
                l_attr = list(self.edges[edge])
                for attr in l_attr:
                    if not self.edges[edge][attr]:
                        del self.edges[edge][attr]

    def remove_attribute(self, attr_name, nodes=True, edges=True):
        """remove an attribute

        Parameters
        ----------
        attr_name : string
            Name of the attribute to remove
        nodes : boolean (default True)
            Remove node attribute if True.
        edges : boolean (default True)
            Remove edge attribute if True.

        Returns
        -------
        None
        """
        if nodes:
            for node in self:
                if attr_name in self.nodes[node]:
                    del self.nodes[node][attr_name]
        if edges:
            for edge in self.edges:
                if attr_name in self.edges[edge]:
                    del self.edges[edge][attr_name]
    