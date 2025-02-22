# -*- coding: utf-8 -*-
"""
Operations on graphs.
"""

import networkx as nx
import pandas as pd
import geopandas as gpd
import geo_nx as gnx

from geo_nx.utils import GeonxError

GEOM = "geometry"
WEIGHT = "weight"
NODE_ID = "node_id"


def compose(geo_g, geo_h):
    """Compose GeoGraph geo_g with geo_h by combining nodes and edges into a single graph.

    The node sets and edges sets do not need to be disjoint.

    Composing preserves the attributes of nodes and edges.
    Attribute values from geo_h take precedent over attribute values from geo_g.

    Parameters
    ----------
    geo_g, geo_h : GeoGraph

    Returns
    -------
    A new GeoGraph with the same type and crs as geo_g

    Notes
    -----
    The crs of geo_g and geo_h have to be identical.
    It is recommended that geo_g and geo_h be either both directed or both undirected.
    """
    if geo_g.graph['crs'] != geo_h.graph['crs']:
        raise GeonxError(
            "geo_g and geo_h must both have the same crs attribute.")
    geo_gh = nx.compose(geo_g, geo_h)
    geo_gh.graph['crs'] = geo_g.graph['crs']
    return geo_gh

def compose_all(geo_list):
    """Compose GeoGraph included in a list by combining nodes and edges into a single graph.

    The node sets and edges sets do not need to be disjoint.

    Composing preserves the attributes of nodes and edges.
    Attribute values from a next GeoGraph take precedent over attribute values from the precedent.

    Parameters
    ----------
    geo_list : list or tuple of GeoGraph

    Returns
    -------
    A new GeoGraph with the same type and crs as geo_g

    Notes
    -----
    The crs of GeoGraphs have to be identical.
    It is recommended that GeoGraphs be either both directed or both undirected.
    """
    if not geo_list:
        return None
    new_geo = geo_list[0]
    for geo in geo_list[1:]:
        new_geo = compose(new_geo, geo)
    return new_geo

def project_graph(nodes_src, target, radius, node_attr, edge_attr):
    """Projection of a list of nodes into a graph.

    The projection create a new graph where nodes are the nodes to project and
    edges are LineString between nodes to project and the nearest node in the graph.

    Parameters
    ----------
    nodes_src : GeoDataFrame
        The GeoDataFrame contains geometry and node_id columns.

    target : GeoDataFrame
        Target is the nodes GeoDataFrame of the graph. It contains geometry and node_id columns.

    radius : float
        Maximal distance of the nearest nodes.

    node_attr : list of string
        Nodes attributes to add in the new graph.

    edge_attr : dict
        The dict is added as an edge attribute to each edge created

    Returns
    -------
    tuple (GeoGraph, GeoDataFrame)
       The GeoGraph is the graph created.
       The GeoDataFrame is the nodes_src with non projected nodes.
    """
    if not set(target[NODE_ID]).isdisjoint(set(nodes_src[NODE_ID])):
        raise GeonxError("node_id of nodes_src and target have to be disjoint")

    target = target[[GEOM, NODE_ID]].copy()
    target["geom_right"] = target[GEOM]
    joined = gpd.sjoin_nearest(
        nodes_src, target, how="left", max_distance=radius, distance_col=WEIGHT
    )
    joined = joined[pd.notna(joined[WEIGHT])]
    nodes_src_other = nodes_src[~nodes_src.index.isin(joined.index)]

    gs_nodes = joined[
        node_attr
        + [
            GEOM,
            "node_id_left",
        ]
    ].rename(columns={"node_id_left": NODE_ID})
    gs_edges = joined[["node_id_left", "node_id_right", WEIGHT, GEOM]]
    gs_edges = gs_edges.rename(
        columns={"node_id_left": "source", "node_id_right": "target"}
    )
    gs_edges[GEOM] = gpd.GeoSeries(gs_edges[GEOM]).shortest_line(
        gpd.GeoSeries(joined["geom_right"])
    )
    for key, value in edge_attr.items():
        gs_edges[key] = value
    gs = gnx.from_geopandas_edgelist(
        gs_edges,
        edge_attr=True,
        node_gdf=gs_nodes,
        node_id=NODE_ID,
        node_attr=node_attr,
    )
    return (gs, nodes_src_other)

def weight_extend(graph, edge, ext_gr, radius=None, n_attribute=None, n_active=None, gr_rev=None):
    """Find the weight of the the path (witch contains edge) between nodes
    included in a projected graph and with minimal weight.

    Parameters
    ----------
    graph : GeoGraph or GeoDiGraph
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
    """
    dist_ext = graph.edges[edge][WEIGHT]
    # radius = max(dist_ext, radius) if radius else dist_ext
    radius = radius if radius else dist_ext
    source = [True, False]
    n_attributes = [n_attribute + '_s', n_attribute + '_e']
    for node, is_source, attribute in zip(edge, source, n_attributes):
        if attribute in graph.nodes[node] and graph.nodes[node][attribute]:
            dist_st = graph.nodes[node][attribute]
        else:
            dist_st = weight_node_to_graph(
                graph, node, ext_gr, is_source, radius=radius,  
                attribute=attribute, active=n_active, gr_rev=gr_rev
            )
        if not dist_st:
            return None
        dist_ext += dist_st
    return dist_ext

def weight_node_to_graph(
    graph, node, ext_gr, is_source, radius=None, attribute=None, active=None, gr_rev=None
):
    """Return the distance between a node and a projected graph.

    Parameters
    ----------
    graph : GeoGraph or GeoDiGraph
    node : int or str
        Origin of the distance measure.
    ext_gr : Graph
        Projected Graph
    is_source : boolean
        True if the node is the source of the edge (directed graph)
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
    """
    #undirected = isinstance(graph, gnx.geodigraph.GeoDiGraph)
    #undirected = graph.to_undirected()
    if radius:
        #ego_gr = nx.ego_graph(graph, node, radius=radius, distance=WEIGHT, center=False).nodes
        ego_gr = nx.ego_graph(graph, node, radius=radius, distance=WEIGHT).nodes
        #ego_gr = nx.ego_graph(undirected, node, radius=radius, distance=WEIGHT).nodes
        #ego_gr = nx.ego_graph(graph, node, radius=radius, distance=WEIGHT, 
        #                      undirected=True).nodes
        #                      undirected=undirected).nodes
        near_gr = [
            nd
            for nd in ego_gr
            if nd in ext_gr
            and nd != node
            and (active not in graph.nodes[nd] or graph.nodes[nd][active])
        ]
        if gr_rev:
            ego_gr = nx.ego_graph(gr_rev, node, radius=radius, distance=WEIGHT).nodes 
            near_gr += [
                nd
                for nd in ego_gr
                if nd in ext_gr
                and nd != node
                and (active not in graph.nodes[nd] or graph.nodes[nd][active])
            ]
    else:
        near_gr = ext_gr
    if is_source:
        dist_st = [
            nx.shortest_path_length(graph, source=nd, target=node, weight=WEIGHT)
            for nd in near_gr
        ]
    else:
        dist_st = [
            nx.shortest_path_length(graph, source=node, target=nd, weight=WEIGHT)
            for nd in near_gr
        ]        
    dist = None if not dist_st else min(dist_st)
    if dist and attribute:
        graph.nodes[node][attribute] = dist
    return dist

def weight_node_to_node(graph, node1, node2):
    """Return the distance between two nodes without path.

    Parameters
    ----------
    graph : GeoGraph or GeoDiGraph
    node1, node2 : int or str
        Nodes used to distance measure.
    """
    return graph.nodes[node1][GEOM].centroid.distance(
        graph.nodes[node2][GEOM].centroid
    )