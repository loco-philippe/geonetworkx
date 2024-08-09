# -*- coding: utf-8 -*-

import shapely
from shapely import LineString, Point
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import networkx as nx
import matplotlib.pyplot as plt
from geonetworkx.geograph import GeoGraph

def from_geopandas_edgelist(edge_gdf, source='source', target='target', 
                            edge_attr=None, node_gdf=None, node_id='node_id', node_attr=None):
    '''Returns a GeoGraph from GeoDataFrame containing an edge list.
    
    The GeoDataFrame should contain at least two columns (node id source, node id target).
    An additional GeoDataFrame is used to load nodes.
    The geometry is a shapely object present in a 'geometry' column of each GeoDataFrame.
    If the geometry is present in only one GeoDataFrame, the other geometry is deduced.
    If the geometries are present in both GeoDataFrame, they should be consistent'''
    
    n_gdf_ok = node_gdf is not None
    e_gdf = edge_gdf.copy()
    n_gdf = node_gdf.copy() if n_gdf_ok else None
    geom = 'geometry'
    weight = 'weight'
    
    match edge_attr:
        case None: 
            new_edge_attr = [geom, weight]
        case True: 
            new_edge_attr = edge_attr
        case list() | tuple():
            new_edge_attr = list(set(edge_attr + [geom, weight]))
        case _:
            new_edge_attr = [geom, weight, edge_attr]
        
    if geom in n_gdf and not geom in e_gdf:
        crs = n_gdf.crs.to_epsg()
        e_gdf = pd.merge(e_gdf, n_gdf.loc[:, (node_id, geom)], how='left', left_on=source, right_on=node_id).rename(columns={geom:'geom_source'})
        e_gdf.pop(node_id) 
        e_gdf = pd.merge(e_gdf, n_gdf.loc[:, (node_id, geom)], how='left', left_on=target, right_on=node_id).rename(columns={geom:'geom_target'})
        e_gdf.pop(node_id) 
        # e_gdfons['geometry'] = pd.Series([LineString([row[3], row[4]]) for row in e_gdf.itertuples()])
        geo_e_gdf = gpd.GeoDataFrame(edge_gdf, geometry = gpd.GeoSeries(e_gdf['geom_source']).shortest_line(gpd.GeoSeries(e_gdf['geom_target'])), crs=crs)
    
    geo_e_gdf[weight] = geo_e_gdf[geom].length
    geo_gr = nx.from_pandas_edgelist(geo_e_gdf, edge_attr=new_edge_attr)
    
    if n_gdf_ok: 
        dic = n_gdf.to_dict(orient='records')
        nx_dic = {row[node_id]: dict(item for item in row.items() if item[0] != node_id) for row in dic}
        #nx_dic = {row[node_id]: dict(item for item in row.items()) for row in dic}
        nx.set_node_attributes(geo_gr, nx_dic)

    crs = geo_e_gdf.crs if geo_e_gdf.crs else (node_gdf.crs if n_gdf_ok else None)
    geo_gr.graph['crs'] = crs.to_epsg()     
    print(geo_gr.graph, GeoGraph(geo_gr).graph)
    return GeoGraph(geo_gr)

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
       Use only nodes specified in nodelist.

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
       Use only nodes defined by node_id specified in nodelist.

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