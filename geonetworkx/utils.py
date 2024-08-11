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
    - adjust: boolean - if True the new point is the geometry's centroid else the projected line point
    
    return 

    - first geometry
    - second geometry
    - intersected point
    - line coordinatefor intersected point'''
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
            return [LineString(coords[:ind+1]), LineString(coords[ind:]), Point(coords[ind]), 0.0]
        if pt_absc > absc:
            cp = line.interpolate(absc)
            new_c = point.coords[0] if adjust else (cp.x, cp.y)
            dist = 0.0 if adjust else point.distance(Point(new_c))
            return [LineString(coords[:ind] + [new_c]), LineString([new_c] + coords[ind:]), Point(new_c), dist]
    return None

def geom_to_crs(geom, crs, new_crs):
    return gpd.GeoSeries([geom], crs=crs).to_crs(new_crs)[0]

def cast_id(node_id):
    if hasattr(node_id, '__iter__') and not isinstance(node_id, str): 
        return list(n_id for n_id in node_id if isinstance(n_id, int))
    try:
        return int(node_id)
    except:
        return node_id