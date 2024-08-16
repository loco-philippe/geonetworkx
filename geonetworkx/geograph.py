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
    - `find_nearest_edge`
    - `find_nearest_node`

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
        """Cut an edge in two edges and insert a new node between each.
        
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

    def plot(self, edges=True, nodes=True, **param):
        '''Plot a GeoGraph.
        
        Generate a plot of the edges GeoDataFrame and nodes GeoDataFrame with matplotlib.
        
        Parameters
        ----------
            
        - edges: boolean - default True
            If True, edges are included in the plot.
        - nodes: boolean - default True
            If True, nodes are included in the plot.
        - param: dict
            `GeoDataFrame.plot` parameters. Parameters are common to edges and nodes. 
            Specific parameters to nodes or edges are preceded by 'n_' or 'e_' (eg 'e_color').
            Default is {'e_edgecolor': 'black', 
                        'n_marker': 'o', 'n_color': 'red', 'n_markersize': 5}
        '''
        param = {'e_edgecolor': 'black', 
                 'n_marker': 'o', 'n_color': 'red', 'n_markersize': 5} | param
        common_param = dict((k, v) for k, v in param.items() if k[:2] not in ['e_', 'n_'] and v)
        edge_param = common_param | dict((k[2:], v) for k, v in param.items() if k[:2] == 'e_' and v)
        node_param = common_param | dict((k[2:], v) for k, v in param.items() if k[:2] == 'n_' and v)
   
        fig, ax = plt.subplots()
        if edges: 
            self.to_geopandas_edgelist().plot(ax=ax, **edge_param)
        if nodes: 
            self.to_geopandas_nodelist().plot(ax=ax, **node_param)
        plt.show()

    def explore(self, refmap=None, edges=True, nodes=True, nodelist=None, 
                layercontrol=False, **param): 
        '''Interactive map based on GeoPandas and folium/leaflet.js

        Generate an interactive leaflet map based on the edges GeoDataFrame and nodes GeoDataFrame.
        
        Parameters
        ----------
            
        - refmap: dict or folium map - default None
            Existing map instance or map defined by a dict (see folium Map keywords) 
            on which to draw the GeoGraph.
        - edges: boolean
            If True, edges are includes in the plot.
        - nodes: boolean
            If True, nodes defined by nodelist are included in the plot.
        - nodelist: list - default None
            Use only nodes specified in nodelist (all if None).
        - layercontrol: boolean - default False
            Add folium.LayerControl to the map if True.
        - param: dict
            `GeoDataFrame.explore` parameters. Parameters are common to edges and nodes. 
            Specific parameters to nodes or edges are preceded by 'n_' or 'e_' (eg 'e_color')
        '''        
        param = {'e_name': 'edges', 'n_name': 'nodes',
                    'e_popup': ['weight'], 'n_popup': None,
                    'e_tooltip': None, 'n_tooltip': None, 
                    'e_color': 'blue', 'n_color': 'black',
                    'n_marker_kwds': {'radius': 2, 'fill': True}} | param
        common_param = dict((k, v) for k, v in param.items() if k[:2] not in ['e_', 'n_'] and v)
        edge_param = common_param | dict((k[2:], v) for k, v in param.items() if k[:2] == 'e_' and v)
        node_param = common_param | dict((k[2:], v) for k, v in param.items() if k[:2] == 'n_' and v)
        
        if isinstance(refmap, dict):
            refmap = folium.Map(**refmap)
        elif refmap is None:
            refmap = folium.Map()
            
        if edges:
            self.to_geopandas_edgelist(nodelist=nodelist).explore(m=refmap, **edge_param)
        if nodes:
            self.to_geopandas_nodelist(nodelist=nodelist).explore(m=refmap, **node_param)
        if layercontrol:
            folium.LayerControl().add_to(refmap)
        return refmap


    def find_nearest_edge(self, geom, max_distance): 
    
        gdf_pt = gpd.GeoDataFrame({'geometry':[geom.centroid]}, crs=self.graph['crs'])
        gdf_ed = self.to_geopandas_edgelist()
        #print(gdf_ed)
        troncons = gdf_pt.sjoin_nearest(gdf_ed, max_distance=max_distance, distance_col='weight')
        if len(troncons):
            troncon = troncons.sort_values(by='weight').iloc[0]
            
            return [cast_id(troncon['source']), cast_id(troncon['target'])]
        return None

    def find_nearest_node(self, geom, max_distance): 
    
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
