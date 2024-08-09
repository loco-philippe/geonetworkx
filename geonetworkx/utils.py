# -*- coding: utf-8 -*-
"""
Functions used for geometry analysis
"""
import shapely
from shapely import LineString, Point
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import networkx as nx

def geo_cut(line, geom, adjust=False):
    ''' Cuts a line in two at the geometry nearest projection point 
    
    - line: LineString or LinearRing to cut
    - geom: geometry to be projected on the line
    - adjust: boolean - if True the new point is the geometry's centroid else the projected line point'''
    line = LineString(line)
    point = geom.centroid
    absc = line.project(point)
    if absc <= 0.0 or absc >= line.length:
        return None
    #print('cut : ', absc, point, line)
    coords = list(line.coords)
    for ind, coord in enumerate(coords):
        pt_absc = line.project(Point(coord))
        if pt_absc == absc:
            coords[ind] = point.coords[0] if adjust else coords[ind]
            return [LineString(coords[:ind+1]), LineString(coords[ind:]), 0.0]
        if pt_absc > absc:
            cp = line.interpolate(absc)
            new_c = point.coords[0] if adjust else (cp.x, cp.y)
            dist = 0.0 if adjust else point.distance(Point(new_c))
            return [LineString(coords[:ind] + [new_c]), LineString([new_c] + coords[ind:]), dist]
    return None

def find_edge(graph, geom, max_distance): 

    gdf_pt = gpd.GeoDataFrame({'geometry':[geom.centroid]}, crs=graph.graph['crs'])
    gdf_ed = graph.to_geopandas_edgelist()
    #print(gdf_ed)
    troncons = gdf_pt.sjoin_nearest(gdf_ed, max_distance=max_distance, distance_col='weight')
    if len(troncons):
        troncon = troncons.sort_values(by='weight').iloc[0]
        return [int(troncon['source']), int(troncon['target'])]
    return None

def geom_to_crs(geom, crs, new_crs):
    return gpd.GeoSeries([geom], crs=crs).to_crs(new_crs)[0]