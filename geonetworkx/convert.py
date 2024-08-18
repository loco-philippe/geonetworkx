# -*- coding: utf-8 -*-
"""
This module contains conversion functions between `geonetworkx.GeoGraph` data and 
`geopandas.GeoDataFrame` data.

The conversion follows two principles:
    
- reversibility: A round-trip return the initial object (lossless conversion),
- optimization: Missing geometries ares reconstructed in two cases. If the nodes are not 
present, nodes are added with a geometry corresponding to edges ends. If 
the geometries edges are not present, a segment between the nodes geometry is added.
 
"""
import math
import pandas as pd
import numpy as np
import geopandas as gpd
import networkx as nx
import geonetworkx as gnx
import geonetworkx.utils as utils

GEOM = 'geometry'
WEIGHT = 'weight'

def from_geopandas_nodelist(node_gdf, node_id=None, node_attr=None):
    '''Convert a GeoDataFrame in an empty GeoGraph (without edges).
    
    The GeoDataFrame should contain at least one column ('geometry') filled with Shapely geometries.
    Columns of the GeoDataFrame are converted in node attributes.
    Rows of the GeoDataFrame are converted in nodes.
    Node id are row numbers (default) or values of a defined column.

    Parameters
    ----------
    node_gdf : GeoDataFrame
        Tabular representation of nodes.
    node_id : String, optional
        Name of the column of node id. if 'node_id' is None (default), node_id is row number.
    node_attr : list, boolean or string - optional
        A valid column name (str or int) or tuple/list of column names that are
        used to retrieve items and add them to the graph as node attributes. 
        If True, all of the remaining columns will be added. If None (default), no node 
        attributes are added to the graph.    
        The 'geometry' column is always converted in 'geometry' attribute.

    Returns
    -------
    GeoGraph
        Empty GeoGraph with nodes of the GeoDataFrame.
    '''
    match node_attr:
        case True: 
            new_node_attr = list(node_gdf.columns)
        case list() | tuple():
            new_node_attr = list(set(node_attr + [GEOM]))
        case str():
            new_node_attr = [GEOM, node_attr]    
        case _: 
            new_node_attr = [GEOM]
    if node_id:
        new_node_attr = list(set(new_node_attr + [node_id]))
    dic = node_gdf.loc[:, new_node_attr].to_dict(orient='records')
    if not node_id or node_id not in node_gdf.columns:
        nx_lis = [(idx, dict(item for item in row.items())) for idx, row in enumerate(dic)]
    else:    
        nx_lis = [(row[node_id], dict(item for item in row.items() if item[0] != node_id and not (isinstance(item[1], float) and math.isnan(item[1])))) for row in dic]
    geo_gr = nx.empty_graph(nx_lis)
    return gnx.GeoGraph(geo_gr, crs=node_gdf.crs)

def from_geopandas_edgelist(edge_gdf, source='source', target='target', 
                            edge_attr=None, node_gdf=None, node_id=None, node_attr=None):
    '''Returns a GeoGraph from GeoDataFrame containing an edge list.
    
    The GeoDataFrame should contain at least three columns (node id source, node id target, geometry).
    An additional GeoDataFrame is used to load nodes with at least a node id column.
    The geometry is a Shapely object present in the 'geometry' column of each GeoDataFrame.
    If the 'geometry' is present in only one GeoDataFrame, the other 'geometry' is deduced.
    If the geometries are present in both GeoDataFrame, they should be consistent
    The 'geometry' column is always converted in 'geometry' attribute.
    
    Parameters
    ----------
    edge_gdf : GeoDataFrame
        Tabular representation of edges.
    source : str (default 'source')
        A valid column name for the source nodes (for the directed case).
    target : str (default 'target')
        A valid column name for the target nodes (for the directed case).
    edge_attr : str, iterable, True, or None
        A valid column name or iterable of column names that are
        used to retrieve items and add them to the GeoGraph as edge attributes.
        If `True`, all columns will be added except `source`, `target`.
        If `None`, no edge attributes are added to the GeoGraph.
    node_gdf : GeoDataFrame, optional
        Tabular representation of nodes.
    node_id : String, optional
        Name of the column of node id. The default is 'node_id'.
    node_attr : list, boolean or string - optional
        A valid column name (str or int) or tuple/list of column names that are
        used to retrieve items and add them to the graph as edge attributes. 
        If True, all of the remaining columns will be added. If None (default), no edge 
        attributes are added to the graph.    

    Returns
    -------
    GeoGraph
        GeoGraph with edges of the GeoDataFrame.'''
    
    n_gdf_ok = node_gdf is not None
    e_gdf = edge_gdf.copy()
    n_gdf = node_gdf.copy() if n_gdf_ok else None
    
    match edge_attr:
        case True: 
            new_edge_attr = True
        case list() | tuple():
            new_edge_attr = list(set(edge_attr + [GEOM, WEIGHT]))
        case str():
            new_edge_attr = [GEOM, WEIGHT, edge_attr]
        case _: 
            new_edge_attr = [GEOM, WEIGHT]

    if n_gdf_ok and GEOM in n_gdf and not GEOM in e_gdf:
        node_id = node_id if node_id else 'node_id'
        e_gdf = utils.add_geometry_edges_from_nodes(e_gdf, source, target, n_gdf, node_id)
    elif not n_gdf_ok:
        n_gdf, e_gdf = utils.nodes_gdf_from_edges_gdf(e_gdf, source=source, target=target)
            
    if WEIGHT not in e_gdf.columns: 
        e_gdf[WEIGHT] = e_gdf[GEOM].length
    geo_gr = nx.from_pandas_edgelist(e_gdf, edge_attr=new_edge_attr)
    
    crs = e_gdf.crs if e_gdf.crs else (n_gdf.crs if n_gdf_ok else None)
    geo_gr.graph['crs'] = crs.to_epsg()    
    node_gr = gnx.from_geopandas_nodelist(n_gdf, node_id=node_id, node_attr=node_attr)
    return gnx.compose(gnx.GeoGraph(geo_gr), node_gr)
        
def to_geopandas_edgelist(graph, source='source', target='target', nodelist=None):
    """Returns the graph edge list as a GeoDataFrame.
    
    Parameters
    ----------
    graph : GeoGraph
        The GeoGraph used to construct the GeoDataFrame.

    source : str or int, optional
        A valid column name (string or integer) for the source nodes (for the
        directed case).

    target : str or int, optional
        A valid column name (string or integer) for the target nodes (for the
        directed case).

    nodelist : list, optional
       Use only nodes specified in nodelist (all if nodelist is None).

    Returns
    -------
    GeoDataFrame
       Graph edge list.
    """
    pd_edgelist = nx.to_pandas_edgelist(graph, source=source, target=target, nodelist=nodelist)
    return gpd.GeoDataFrame(pd_edgelist, crs=graph.graph['crs'])

def to_geopandas_nodelist(graph, node_id='node_id', nodelist=None):
    """Returns the graph node list as a GeoDataFrame.
    
    Parameters
    ----------
    graph : GeoGraph
        The GeoGraph used to construct the GeoDataFrame.

    node_id : str, optional
        A valid column name for the nodelist parameter.

    nodelist : list, optional
       Use only nodes defined by node_id specified in nodelist (all if nodelist is None).

    Returns
    -------
    GeoDataFrame
       Graph node list.
    """    
    nodes = pd.DataFrame.from_records(np.array(graph.nodes.data())[:,1])
    nodes[node_id]= pd.Series(list(graph.nodes))
    if nodelist:
        nodes = nodes.set_index(node_id).loc[nodelist].reset_index()
    return gpd.GeoDataFrame(nodes, crs=graph.graph['crs'])