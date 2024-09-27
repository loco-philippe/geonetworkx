# -*- coding: utf-8 -*-
"""
Functions used for geometry analysis
"""
from shapely import LineString, Point
import pandas as pd
import geopandas as gpd

GEOM = 'geometry'
WEIGHT = 'weight'


def geo_cut(line, geom, adjust=False):
    ''' Cuts a line in two at the geometry nearest projection point

    Parameters
    ----------

    - line: shapely LineString or LinearRing
        Line to cut.
    - geom: shapely geometry
        Geometry to be projected on the line (centroid projection).
    - adjust: boolean
        If True, the new point is the geometry's centroid else the projected line point

    Returns
    -------
    - tuple (four values)
        - first geometry (shapely LineString)
        - second geometry (shapely LineString)
        - intersected point (shapely Point)
        - line coordinate for intersected point (float)
    '''
    line = LineString(line)
    point = geom.centroid
    absc = line.project(point)
    if absc <= 0.0 or absc >= line.length:
        return None
    coords = list(line.coords)
    for ind, coord in enumerate(coords):
        pt_absc = line.project(Point(coord))
        if pt_absc == absc:
            coords[ind] = point.coords[0] if adjust else coords[ind]
            return [LineString(coords[:ind+1]), LineString(coords[ind:]), Point(coords[ind]), 0.0]
        if pt_absc > absc:
            cp = line.interpolate(absc)
            new_c = point.coords[0] if adjust else (cp.x, cp.y)
            dist = 0.0 if adjust else point.distance(Point(new_c))
            return [LineString(coords[:ind] + [new_c]),
                    LineString([new_c] + coords[ind:]), Point(new_c), dist]
    return None


def nodes_gdf_from_edges_gdf(e_gdf, source=None, target=None):
    """create a nodes GeoDataFrame from an edges GeoDataFrame.

    A node geometry is one of the ends (Point) of the edge geometry (LineString).
    If source and target are not present in e_gdf, they are added.

    Parameters
    ----------
    e_gdf : GeoDataFrame
        Tabular representation of edges.
    source : str (default None)
        A valid column name for the source nodes (for the directed case).
    target : str (default 'target')
        A valid column name for the target nodes (for the directed case).

    Returns
    -------
    tuple of two GeoDataFrame
       n_gdf: Tabular representation of nodes (created),
       e_gdf: Tabular representation of nodes (addition of source and target columns),
    """
    crs = e_gdf.crs.to_epsg()
    node_id = 'node_id'
    e_gdf["source_geo"] = e_gdf[GEOM].apply(lambda ls: ls.boundary.geoms[0])
    e_gdf["target_geo"] = e_gdf[GEOM].apply(lambda ls: ls.boundary.geoms[1])

    if source in e_gdf.columns:
        e_gdf_source = e_gdf.loc[:, [source, "source_geo"]].rename(
            columns={source: node_id, "source_geo": GEOM})
        e_gdf_target = e_gdf.loc[:, [target, "target_geo"]].rename(
            columns={target: node_id, "target_geo": GEOM})
        n_gdf = pd.concat([e_gdf_source, e_gdf_target]).drop_duplicates()
    else:
        n_gdf = pd.concat([e_gdf["source_geo"], e_gdf["target_geo"]]
                          ).drop_duplicates().reset_index(drop=True)
        nodidx = pd.Series(n_gdf.index, index=n_gdf)
        e_gdf = e_gdf.join(nodidx.rename(source), on="source_geo", how='left')
        e_gdf = e_gdf.join(nodidx.rename(target), on="target_geo", how='left')
        n_gdf = gpd.GeoDataFrame({GEOM: n_gdf, node_id: n_gdf.index}, crs=crs)
    del e_gdf["source_geo"], e_gdf["target_geo"]
    return (n_gdf, e_gdf)


def add_geometry_edges_from_nodes(e_gdf, source, target, n_gdf, node_id):
    """add a geometry column in an edges GeoDataFrame from geometry nodes.

    An edge geometry is a segment (LineString) between the points (geometry.centroid)
    of the nodes geometries.

    Parameters
    ----------
    e_gdf : GeoDataFrame
        Tabular representation of edges.
    n_gdf : GeoDataFrame
        Tabular representation of nodes.
    node_id : String
        Name of the column of node id.

    Returns
    -------
    GeoDataFrame
       Graph edge with additional 'geometry' column.
    """
    crs = n_gdf.crs.to_epsg()
    e_gdf = pd.merge(e_gdf, n_gdf.loc[:, (node_id, GEOM)], how='left', left_on=source,
                     right_on=node_id).rename(columns={GEOM: 'geom_source'})
    e_gdf.pop(node_id)
    e_gdf = pd.merge(e_gdf, n_gdf.loc[:, (node_id, GEOM)], how='left', left_on=target,
                     right_on=node_id).rename(columns={GEOM: 'geom_target'})
    e_gdf.pop(node_id)
    gs_src = gpd.GeoSeries(e_gdf['geom_source'])
    gs_tgt = gpd.GeoSeries(e_gdf['geom_target'])
    e_gdf = gpd.GeoDataFrame(
        e_gdf, geometry=gs_src.shortest_line(gs_tgt), crs=crs)
    del e_gdf["geom_source"], e_gdf["geom_target"]
    return e_gdf


def geom_to_crs(geom, crs, new_crs):
    '''convert geometry coordinates from a CRS to another CRS

    Parameters
    ----------
    geom : Shapely geometry
        Geometry to convert.
    crs : geopandas CRS
        CRS of the existing geometry.
    new_crs : geopandas CRS
        CRS to apply to geometry.

    Returns
    -------
    Shapely geometry
       Geometry with coordinates defined in the new CRS.
'''
    return gpd.GeoSeries([geom], crs=crs).to_crs(new_crs)[0]


def cast_id(node_id, only_int=False):
    '''replace number string as integer in a single or an iterable.

    If option is activate, return only integer.

    Parameters
    ----------
    node_id : Single or iterable string/integer
        Value to convert
    only_int : Boolean
        If True return only integer.

    Returns
    -------
    List
       list of int (if only_int) or list of int/string.
    '''
    if hasattr(node_id, '__iter__') and not isinstance(node_id, str):
        cast_list = list(cast_id(n_id, only_int=only_int) for n_id in node_id)
        return [val for val in cast_list if val is not None]
    try:
        return int(node_id)
    except (ValueError, TypeError):
        return None if only_int else node_id
