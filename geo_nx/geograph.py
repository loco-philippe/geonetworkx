# -*- coding: utf-8 -*-
"""
This module contains the `GeoGraph` class.
"""

import geopandas as gpd
import folium
import networkx as nx
import matplotlib.pyplot as plt
from shapely import LineString
from geo_nx.convert import to_geopandas_edgelist
from geo_nx.convert import to_geopandas_nodelist
from geo_nx.utils import geo_cut, cast_id

GEOM = 'geometry'
WEIGHT = 'weight'
NODE_ID = 'node_id'


class GeoGraph(nx.Graph):
    """This class analyses geospatial graphs.

    A geospatial graph is a graph where nodes and edges are related to a geometry.

    A GeoGraph is a NetworkX Graph with a shapely geometry as egde attribute and node attribute.

    The GeoGraph 'crs' attribute defines the coordinate reference used.

    *instance methods*

    - `insert_node`
    - `project_node`
    - `to_geopandas_edgelist`
    - `to_geopandas_nodelist`
    - `plot`
    - `explore`
    - `find_nearest_edge`
    - `find_nearest_node`
    - `weight_extend`

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

    def merge_node(self, add_node, graph, radius):
        '''Find the nearest node of 'graph' and update attr

        Parameters
        ----------

        add_node: id
            Id of the node to project.
        graph: GeoGraph
            Graph to connect to the add_node.
        radius : float
            Maximum distance between add_node and graph.

        Returns
        -------

        dist: float
            Distance between add_node and graph (None if distance > radius).
          '''
        geo_st = self.nodes[add_node][GEOM].centroid
        id_node = graph.find_nearest_node(geo_st, radius) # recherche d'un noeud à moins de 3 km
        if not id_node:
            return None
        dis1 = geo_st.distance(graph.nodes[id_node][GEOM])
        graph.add_node(id_node, **self.nodes[add_node])
        return dis1

    def project_node(self, add_node, graph, radius, att_edge=None, update_node=False):
        '''Add an external node in a Graph (update the nearest node of 'graph' or add a 
        LineString edge between 'add_node' and the nearest node of 'graph'. 
        The LineString length has to be lower than radius.

        Parameters
        ----------

        add_node: id
            Id of the node to project.
        att_edge: dict
            Attributes of the added edge.
        graph: GeoGraph
            Graph to connect to the add_node.
        radius: float
            Maximum distance between add_node and graph.
        update_node: boolean
            If True, 
        Returns
        -------

        dist: float
            Distance between add_node and graph (None if distance > radius).
          '''
        att_edge = {} if not att_edge else att_edge
        geo_st = self.nodes[add_node][GEOM].centroid
        id_node = graph.find_nearest_node(geo_st, radius) # recherche du noeud proche
        if not id_node:
            return None
        dis1 = geo_st.distance(graph.nodes[id_node][GEOM])
        if update_node:
            graph.add_node(id_node, **(self.nodes[add_node] | {GEOM:graph.nodes[id_node][GEOM]}))            
        else:
            geo1 = LineString([graph.nodes[id_node][GEOM], geo_st])
            self.add_edge(id_node, add_node, **(att_edge | {GEOM:geo1, WEIGHT: dis1})) # ajout du lien entre la station et le noeud routier
        return dis1
    
    def erase_node(self, id_node, adjust=False):
        return
        
    def insert_node(self, geom, id_node, id_edge, att_node={}, adjust=False):
        """Cut an edge in two edges and insert a new node between each.

        The 'geometry' attribute of the two edges and the new node is build from the geometry of
        the initial edge and the parameter geometry.

        Parameters
        ----------

        id_node: id
            Id of the inserted node.
        att_node: dict
            Attributes of the inserted node.
        id_edge: tuple of two id_node
            Id of the cuted edge.
        geom: shapely geometry
            Geometry to be projected on the edge line (centroid projection).
        adjust: boolean
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
        new_geo = geo_cut(att_edge[GEOM], geom, adjust=adjust)
        if not new_geo:
            return None
        geo1, geo2, intersect, dist = new_geo

        edg_0 = self.nodes[id_edge[0]][GEOM].coords[0]
        first = id_edge[0] if edg_0 == geo1.coords[0] else id_edge[1]
        last = id_edge[1] if first == id_edge[0] else id_edge[0]

        self.add_node(id_node, **(att_node | {GEOM: intersect}))
        self.add_edge(first, id_node, **(att_edge |
                      {GEOM: geo1, WEIGHT: geo1.length}))
        self.add_edge(id_node, last, **(att_edge |
                      {GEOM: geo2, WEIGHT: geo2.length}))
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

        edges: boolean - default True
            If True, edges are included in the plot.
        nodes: boolean - default True
            If True, nodes are included in the plot.
        param: dict
            `GeoDataFrame.plot` parameters. Parameters are common to edges and nodes.
            Specific parameters to nodes or edges are preceded by *n_* or *e_* (eg 'e_color').
            Default is {'e_edgecolor': 'black', 'n_marker': 'o', 'n_color': 'red',
            'n_markersize': 5}
        '''
        param = {'e_edgecolor': 'black',
                 'n_marker': 'o', 'n_color': 'red', 'n_markersize': 5} | param
        common_param = dict((k, v) for k, v in param.items()
                            if k[:2] not in ['e_', 'n_'] and v)
        edge_param = common_param | dict(
            (k[2:], v) for k, v in param.items() if k[:2] == 'e_' and v)
        node_param = common_param | dict(
            (k[2:], v) for k, v in param.items() if k[:2] == 'n_' and v)

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

        refmap: dict or folium map - default None
            Existing map instance or map defined by a dict (see folium Map keywords)
            on which to draw the GeoGraph.
        edges: boolean
            If True, edges are includes in the plot.
        nodes: boolean
            If True, nodes defined by nodelist are included in the plot.
        nodelist: list - default None
            Use only nodes specified in nodelist (all if None).
        layercontrol: boolean - default False
            Add folium.LayerControl to the map if True.
        param: dict
            `GeoDataFrame.explore` parameters. Parameters are common to edges and nodes.
            Specific parameters to nodes or edges are preceded by *n_* or *e_* (eg 'e_color')
        '''
        param = {'e_name': 'edges', 'n_name': 'nodes',
                 'e_popup': ['weight'], 'n_popup': None,
                 'e_tooltip': None, 'n_tooltip': None,
                 'e_color': 'blue', 'n_color': 'black',
                 'n_marker_kwds': {'radius': 2, 'fill': True}} | param
        common_param = dict((k, v) for k, v in param.items()
                            if k[:2] not in ['e_', 'n_'] and v)
        edge_param = common_param | dict(
            (k[2:], v) for k, v in param.items() if k[:2] == 'e_' and v)
        node_param = common_param | dict(
            (k[2:], v) for k, v in param.items() if k[:2] == 'n_' and v)

        if isinstance(refmap, dict):
            refmap = folium.Map(**refmap)
        elif refmap is None:
            refmap = folium.Map()

        if edges and self.edges:
            self.to_geopandas_edgelist(
                nodelist=nodelist).explore(m=refmap, **edge_param)
        if nodes and self.nodes:
            self.to_geopandas_nodelist(
                nodelist=nodelist).explore(m=refmap, **node_param)
        if layercontrol:
            folium.LayerControl().add_to(refmap)
        return refmap

    def find_nearest_edge(self, geom, max_distance):
        '''Find the closest edge to a geometry

        Spatial join based on the distance between given geometry and edges geometries.

        Results will include a single output records (even in case of multiple
        nearest and equidistant geometries).

        Parameters
        ----------
        geom : Shapely Geometry
            Geometry used in the spatial join.
        max_distance : float
            Maximum distance within which to query for nearest geometry.

        Returns
        -------
        list
            id of the nearest edge (list of two id_node)
        '''
        gdf_pt = gpd.GeoDataFrame(
            {GEOM: [geom.centroid]}, crs=self.graph['crs'])
        gdf_ed = self.to_geopandas_edgelist()
        troncons = gdf_pt.sjoin_nearest(
            gdf_ed, max_distance=max_distance, distance_col=WEIGHT)
        if len(troncons):
            troncon = troncons.sort_values(by=WEIGHT).iloc[0]
            return [cast_id(troncon['source']), cast_id(troncon['target'])]
        return None

    def find_nearest_node(self, geom, max_distance):
        '''Find the closest node to a geometry.

        Spatial join based on the distance between given geometry and nodes geometries.

        Results will include a single output records (even in case of multiple
        nearest and equidistant geometries).

        Parameters
        ----------
        geom : Shapely Geometry
            Geometry used in the spatial join.
        max_distance : float
            Maximum distance within which to query for nearest geometry.

        Returns
        -------
        list
            id of the nearest edge (list of two id_node)
        '''
        gdf_pt = gpd.GeoDataFrame(
            {GEOM: [geom.centroid]}, crs=self.graph['crs'])
        gdf_no = self.to_geopandas_nodelist()
        noeuds = gdf_pt.sjoin_nearest(
            gdf_no, max_distance=max_distance, distance_col=WEIGHT)
        if len(noeuds):
            noeud = noeuds.sort_values(by=WEIGHT).iloc[0]
            return cast_id(noeud[NODE_ID])
        return None

    def weight_extend(self, edge, ext_gr, radius=None, n_attribute=None, n_active=None):
        '''Find the path (witch contains edge) between nodes included in a projected graph and with minimal weight.

        Parameters
        ----------
        edge : tuple
            Edge to extend in the projected graph.
        ext_gr : Graph
            Projected Graph.
        radius : float (default None)
            radius used to find the nearest external node for each node of the edge.
            If None, the radius used is the weight of the edge.
        n_attribute : str (default None)
            Node attribute to store node projected distance.
        n_active : str (default None)
            Node attribute that indicates the validity (boolean) of the node.
        Returns
        -------
        float
            extended weight
        '''
        dist_ext = self.edges[edge][WEIGHT]
        radius = max(dist_ext, radius) if radius else dist_ext
        for node in edge:
            if n_attribute in self.nodes[node] and self.nodes[node][n_attribute]:
                dist_st = self.nodes[node][n_attribute]
            else:
                dist_st = self.weight_node_to_graph(node, ext_gr, radius=radius,
                                                    attribute=n_attribute, active=n_active)
            if not dist_st:
                return None
            dist_ext += dist_st
        return dist_ext

    def weight_node_to_graph(self, node, ext_gr, radius=None, attribute=None, active=None):
        '''Return the distance between a node and a projected graph.

        Parameters
        ----------
        node : int or str
            Origin of the distance measure.
        ext_gr : Graph
            Projected Graph
        radius : float (default None)
            value used to filter projected nodes before analyse.
            If None, all the projected graph is used.
        attribute : int or str (default None)
            Node attribute to store resulted distance
        active : str (default None)
            ext_gr node attribute that indicates the validity (boolean) of the node.
        Returns
        -------
        float
            distance between the node and the projected graph
        '''
        if radius:
            ego_gr = nx.ego_graph(self, node, radius=radius, distance=WEIGHT).nodes
            near_gr = [nd for nd in ego_gr if nd in ext_gr and nd != node and
                       (active not in self.nodes[nd] or self.nodes[nd][active])]
        else:
            near_gr = ext_gr
        dist_st = [nx.shortest_path_length(self, source=node, target=nd, weight=WEIGHT) 
                   for nd in near_gr]
        dist = None if not dist_st else min(dist_st)
        if dist and attribute:
            self.nodes[node][attribute] = dist
        return  dist

class GeoGraphError(Exception):
    """GeoGraph Exception"""
