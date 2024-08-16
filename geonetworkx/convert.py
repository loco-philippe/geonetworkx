# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import geopandas as gpd
import networkx as nx
import geonetworkx as gnx

def from_geopandas_nodelist(node_gdf, node_id=None, node_attr=None):
    geom = 'geometry'
    match node_attr:
        case True: 
            new_node_attr = node_attr
        case list() | tuple():
            new_node_attr = list(set(node_attr + [geom]))
        case str():
            new_node_attr = [geom, node_attr]    
        case _: 
            new_node_attr = [geom]
    dic = node_gdf.loc[:, new_node_attr].to_dict(orient='records')
    if not node_id:
        nx_lis = [(idx, dict(item for item in row.items())) for idx, row in enumerate(dic)]
    else:    
        nx_lis = [(row[node_id], dict(item for item in row.items() if item[0] != node_id)) for row in dic]
    geo_gr = nx.empty_graph(nx_lis)
    return gnx.GeoGraph(geo_gr, crs=node_gdf.crs)

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
        case True: 
            new_edge_attr = True
        case list() | tuple():
            new_edge_attr = list(set(edge_attr + [geom, weight]))
        case str():
            new_edge_attr = [geom, weight, edge_attr]
        case _: 
            new_edge_attr = [geom, weight]
    if n_gdf_ok and geom in n_gdf and not geom in e_gdf:
        crs = n_gdf.crs.to_epsg()
        e_gdf = pd.merge(e_gdf, n_gdf.loc[:, (node_id, geom)], how='left', left_on=source, right_on=node_id).rename(columns={geom:'geom_source'})
        e_gdf.pop(node_id) 
        e_gdf = pd.merge(e_gdf, n_gdf.loc[:, (node_id, geom)], how='left', left_on=target, right_on=node_id).rename(columns={geom:'geom_target'})
        e_gdf.pop(node_id) 
        # e_gdfons['geometry'] = pd.Series([LineString([row[3], row[4]]) for row in e_gdf.itertuples()])
        e_gdf = gpd.GeoDataFrame(edge_gdf, geometry = gpd.GeoSeries(e_gdf['geom_source']).shortest_line(gpd.GeoSeries(e_gdf['geom_target'])), crs=crs)
    elif not n_gdf_ok:
        crs = e_gdf.crs.to_epsg()
        e_gdf["source_geo"] = e_gdf["geometry"].apply(lambda ls: ls.boundary.geoms[0])
        e_gdf["target_geo"] = e_gdf["geometry"].apply(lambda ls: ls.boundary.geoms[1])
        
        if source in e_gdf.columns:
            e_gdf_source = e_gdf.loc[:,[source, "source_geo"]].rename(columns={source: node_id, "source_geo": geom})
            e_gdf_target = e_gdf.loc[:,[target, "target_geo"]].rename(columns={target: node_id, "target_geo": geom})
            n_gdf = pd.concat([e_gdf_source, e_gdf_target]).drop_duplicates()
        else:
            n_gdf = pd.concat([e_gdf["source_geo"], e_gdf["target_geo"]]).drop_duplicates().reset_index(drop=True)
            nodidx =pd.Series(n_gdf.index, index=n_gdf)
            e_gdf = e_gdf.join(nodidx.rename(source), on="source_geo", how='left')
            e_gdf = e_gdf.join(nodidx.rename(target), on="target_geo", how='left')
            n_gdf = gpd.GeoDataFrame({geom: n_gdf, node_id: n_gdf.index}, crs=crs)
        del e_gdf["source_geo"], e_gdf["target_geo"]
            
    if weight not in e_gdf.columns: 
        e_gdf[weight] = e_gdf[geom].length
    geo_gr = nx.from_pandas_edgelist(e_gdf, edge_attr=new_edge_attr)
    
    dic = n_gdf.to_dict(orient='records')
    nx_dic = {row[node_id]: dict(item for item in row.items() if item[0] != node_id) for row in dic}    
    nx.set_node_attributes(geo_gr, nx_dic)

    crs = e_gdf.crs if e_gdf.crs else (n_gdf.crs if n_gdf_ok else None)
    geo_gr.graph['crs'] = crs.to_epsg()    
    #node_gr = gnx.from_geopandas_nodelist(n_gdf, node_id=node_id, node_attr=node_attr)
    #return gnx.compose(gnx.GeoGraph(geo_gr), node_gr)
    return gnx.GeoGraph(geo_gr)

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