# -*- coding: utf-8 -*-
"""
This module contains the `GeoGraph` class.
"""
import geo_nx as gnx
import geopandas as gpd
import folium
import networkx as nx
from shapely import LineString
from geo_nx.convert import to_geopandas_edgelist, to_geopandas_nodelist
from geo_nx.convert import explore
from geo_nx.utils import geo_cut, cast_id, geo_merge
from geo_nx.algorithms import weight_extend, weight_node_to_graph
from geo_nx.geogr import GeoGr

GEOM = "geometry"
WEIGHT = "weight"
NODE_ID = "node_id"


class GeoGraph(nx.Graph, GeoGr):
    """This class analyses geospatial graphs.

    A geospatial graph is a graph where nodes and edges are related to a geometry.

    A GeoGraph is a NetworkX Graph with a shapely geometry as egde attribute and node attribute.

    The GeoGraph 'crs' attribute defines the coordinate reference used.

    *instance methods*

    - `to_directed`    
    - `insert_node`
    - `erase_linear_nodes`
    - `project_node`
    - `to_geopandas_edgelist`
    - `to_geopandas_nodelist`
    - `plot`
    - `explore`
    - `find_nearest_edge`
    - `find_nearest_node`
    - `weight_extend`
    - `clean_attributes`

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
        if "crs" not in self.graph:
            self.graph["crs"] = None

    def merge_node(self, add_node, graph, radius):
        """Find the nearest node of 'graph' and update attr

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
        """
        geo_st = self.nodes[add_node][GEOM].centroid
        id_node = graph.find_nearest_node(geo_st, radius)
        if not id_node:
            return None
        dis1 = geo_st.distance(graph.nodes[id_node][GEOM])
        graph.add_node(id_node, **self.nodes[add_node])
        return dis1

    def project_node(
        self,
        add_node,
        graph,
        radius,
        att_edge=None,
        update_node=False,
        target_node=None,
    ):
        """Add an external node in a Graph.

        Update the nearest node of 'graph' or
        add a LineString edge between 'add_node' and the nearest node of 'graph'.
        The LineString length has to be lower than radius.

        Parameters
        ----------

        add_node: id
            Id of the node to project.
        target_node: id
            Id of the graph node to project add_node. If None, the nearest is used.
        att_edge: dict
            Attributes of the added edge.
        graph: GeoGraph
            Graph to connect to the add_node.
        radius: float
            Maximum distance between add_node and graph.
        update_node: boolean
            If True, the nearest node is updated with 'add_node' attributes.
            If False, a LineString edge is added.

        Returns
        -------

        dist: float
            Distance between add_node and graph (None if distance > radius).
        """
        att_edge = {} if not att_edge else att_edge
        geo_st = self.nodes[add_node][GEOM].centroid
        id_node = (
            target_node if target_node else graph.find_nearest_node(geo_st, radius)
        )
        if not id_node:
            return None
        dis1 = geo_st.distance(graph.nodes[id_node][GEOM])
        if update_node:
            graph.add_node(
                id_node, **(self.nodes[add_node] | {GEOM: graph.nodes[id_node][GEOM]})
            )
        else:
            geo1 = LineString([graph.nodes[id_node][GEOM], geo_st])
            self.add_edge(id_node, add_node, **(att_edge | {GEOM: geo1, WEIGHT: dis1}))
        return dis1

    def erase_linear_nodes(self, id_node=None, adjust=True, keep_attr=None):
        """Remove linear nodes.

        A linear node is a node with two adjacent nodes. The two edges are replaced by
        a single one where:
        - the geometry is the concatenation of the two geometries,
        - the other attributes are merged
        The node is removed.
        If an edge is already existing or if somme attributes are different, the method is not applied.

        Parameters
        ----------

        id_node: None, id or list of id (default None)
            id : Id of the node to remove
            list of Id : list of id of nodes to remove
            None : remove all the linear nodes
        adjust: boolean (default True)
            If False, the result is None if the boundaries are disjoint
        attr: list (default None)
            attr attributes have to be identical

        Returns
        -------

        boolean
            True if the the graph is changed.
        """
        len_nodes = len(self)
        nodes = (
            list(self.nodes)
            if not id_node
            else (id_node if isinstance(id_node, list) else [id_node])
        )
        keep_attr = (
            []
            if not keep_attr
            else (keep_attr if isinstance(keep_attr, list) else [keep_attr])
        )
        for node in nodes:
            keep_node = False
            adj_nodes = list(self.adj[node])
            if len(adj_nodes) != 2 or adj_nodes in self.edges:
                continue
            node1, node2 = adj_nodes
            edge1 = self.edges[node, node1]
            edge2 = self.edges[node, node2]
            for att in keep_attr:
                if edge1[att] != edge2[att]:
                    keep_node = True
                    break
            if keep_node:
                continue
            attr = edge1 | edge2
            attr[GEOM] = geo_merge(edge1[GEOM], edge2[GEOM], adjust=adjust)
            attr[WEIGHT] = attr[GEOM].length
            self.add_edge(node1, node2, **attr)
            self.remove_node(node)
        return len(self) != len_nodes

    def insert_node(self, geom, id_node, id_edge, att_node=None, adjust=False):
        """Cut an edge in two edges and insert a new node between each.

        The 'geometry' attribute of the two edges and the new node is build from the geometry of
        the initial edge and the parameter geometry.

        Parameters
        ----------

        id_node: id
            Id of the inserted node.
        att_node: dict (default None)
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
        att_node = att_node if att_node else {}
        new_geo = geo_cut(att_edge[GEOM], geom, adjust=adjust)
        if not new_geo:
            return None
        geo1, geo2, intersect, dist = new_geo

        edg_0 = self.nodes[id_edge[0]][GEOM].coords[0]
        first = id_edge[0] if edg_0 == geo1.coords[0] else id_edge[1]
        last = id_edge[1] if first == id_edge[0] else id_edge[0]

        self.add_node(id_node, **(att_node | {GEOM: intersect}))
        self.add_edge(first, id_node, **(att_edge | {GEOM: geo1, WEIGHT: geo1.length}))
        self.add_edge(id_node, last, **(att_edge | {GEOM: geo2, WEIGHT: geo2.length}))
        self.remove_edge(*id_edge)

        return dist

    def to_directed(self):
        """Returns an undirected copy of the graph."""
        return gnx.GeoDiGraph(super().to_directed(self), crs=self.graph["crs"])
    
    def find_nearest_edge(self, geom, max_distance):
        """Find the closest edge to a geometry

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
        """
        gdf_pt = gpd.GeoDataFrame({GEOM: [geom.centroid]}, crs=self.graph["crs"])
        gdf_ed = self.to_geopandas_edgelist()
        troncons = gdf_pt.sjoin_nearest(
            gdf_ed, max_distance=max_distance, distance_col=WEIGHT
        )
        if len(troncons):
            troncon = troncons.sort_values(by=WEIGHT).iloc[0]
            return [cast_id(troncon["source"]), cast_id(troncon["target"])]
        return None

    def find_nearest_node(self, geom, max_distance):
        """Find the closest node to a geometry.

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
        """
        gdf_pt = gpd.GeoDataFrame({GEOM: [geom.centroid]}, crs=self.graph["crs"])
        gdf_no = self.to_geopandas_nodelist()
        noeuds = gdf_pt.sjoin_nearest(
            gdf_no, max_distance=max_distance, distance_col=WEIGHT
        )
        if len(noeuds):
            noeud = noeuds.sort_values(by=WEIGHT).iloc[0]
            return cast_id(noeud[NODE_ID])
        return None
