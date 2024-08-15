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
    """This class analyses geospatial graphs.
    A geospatial graph is a graph where nodes and edges are related to a geometry.
    A GeoGraph is a NetworkX Graph with a shapely geometry as egde attribute and node attribute.
    The GeoGraph 'crs' attribute defines the coordinate reference used.  

    *instance methods*

    - `insert_node`
    - `to_geopandas_edgelist`
    - `to_geopandas_nodelist`
    - `plot`
    - `explore`
    - `path_view`
    - `find_edge`
    - `find_node`

    """

    def __init__(self, incoming_graph_data=None, **attr):
        """The initialization of a GeoGraph is identical to a Graph initialization.
        (with the addition of the creation of a 'crs' attribute - default : None).
        
        The 'geometry' attribute is mandatory for the GeoGraph methods (eg. to_geopandas_edgelist)

        Examples
        --------
        Create an empty graph structure (a "null graph") with no nodes and no edges.
        
        >>> G = nx.Graph()
        """
        super().__init__(incoming_graph_data, **attr)
        if 'crs' not in self.graph:
            self.graph['crs'] = None

    def insert_node(self, geom, id_node, id_edge, att_node={}, adjust=False):
        """The insert_node method cut an edge in two edges and insert a new node between each.
        The 'geometry' attribute of the two edges and the new node is build from the geometry of 
        the initial edge and the parameter geometry.
        
        Parameters
        ----------
            
        - id_node: id
            Id of the inserted node.
        - att_node: dict
            Attributes of the inserted node.
        - id_edge: tuple of two id_node
            Id of the cuted edge.
        - geom: shapely geometry
            Geometry to be projected on the edge line (centroid projection).
        - adjust: boolean
            If True, the new point is the geometry's centroid else the projected line point     
            
        Returns
        -------
        
        dist: float
            Abcissa of the new node in the cuted edge geometry.
            
        Note
        ----
        
        This method is available only with LineString as edge geometry.
        """
        att_edge = self.edges[*id_edge]
        new_geo = geo_cut(att_edge['geometry'], geom, adjust=adjust)
        if not new_geo:
            return None
        geo1, geo2, intersect, dist = new_geo
        
        edg_0 = self.nodes[id_edge[0]]['geometry'].coords[0]
        first = id_edge[0] if edg_0 == geo1.coords[0] else id_edge[1]
        last = id_edge[1] if first == id_edge[0] else id_edge[0]
        
        self.add_node(id_node, **(att_node | {'geometry': intersect}))
        self.add_edge(first, id_node, **(att_edge | {'geometry': geo1, 'weight': geo1.length}))
        self.add_edge(id_node, last, **(att_edge | {'geometry': geo2, 'weight': geo2.length}))
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

    def explore(self, refmap=None, edges=True, nodes=True, nodelist=None, 
                layercontrol=False, **expparam): 
        
        expparam = {'e_name': 'edges', 'n_name': 'nodes',
                    'e_popup': ['weight'], 'n_popup': None,
                    'e_tooltip': None, 'n_tooltip': None, 
                    'e_color': 'blue', 'n_color': 'black',
                    'n_marker_kwds': {'radius': 2, 'fill': True}}   | expparam
        edgeparam = dict((k[2:], v) for k, v in expparam.items() if k[:2] == 'e_' and v)
        nodeparam = dict((k[2:], v) for k, v in expparam.items() if k[:2] == 'n_' and v)
        
        if isinstance(refmap, dict):
            refmap = folium.Map(**refmap)
        
        if edges:
            if refmap:
                self.to_geopandas_edgelist(nodelist=nodelist).explore(m=refmap, **edgeparam)
            else:
                refmap = self.to_geopandas_edgelist(nodelist=nodelist).explore(**edgeparam)
        if nodes:
            if refmap:
                self.to_geopandas_nodelist(nodelist=nodelist).explore(m=refmap, **nodeparam)
            else:
                refmap = self.to_geopandas_nodelist(nodelist=nodelist).explore(**nodeparam)
        if layercontrol:
            folium.LayerControl().add_to(refmap)
        return refmap

    def path_view(self, nodelist):

        def filter_node(node):
            return node in nodelist
        def filter_edge(node1, node2):
            return node1 in nodelist and node2 in nodelist
        return nx.subgraph_view(self, filter_node=filter_node, filter_edge=filter_edge)

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
