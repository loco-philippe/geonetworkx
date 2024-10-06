# -*- coding: utf-8 -*-
"""
Test geo_nx
"""
import unittest

from shapely import LineString, Point
import geopandas as gpd
import geo_nx as gnx 
import networkx as nx 
import pandas as pd
import geo_nx.utils as utils
from networkx.utils import graphs_equal

paris = Point(2.3514, 48.8575)
lyon = Point(4.8357, 45.7640)
marseille = Point(5.3691, 43.3026)
bordeaux = Point(-0.56667, 44.833328)

class TestGeoGraph(unittest.TestCase):
    """tests GeoGraph class"""

    def test_geograph(self):
        """tests GeoGraph"""
        simplemap = gpd.GeoDataFrame({'geometry': [LineString([paris, lyon]), LineString([lyon, marseille]), 
            LineString([paris, bordeaux]), LineString([bordeaux, marseille])]}, crs=4326).to_crs(2154)
        gr_simplemap = gnx.from_geopandas_edgelist(simplemap)
        self.assertTrue(len(gr_simplemap.nodes) == len(gr_simplemap.nodes) == len(simplemap))
        gr_simplemap.nodes[0]['city'] = 'paris'
        gr_simplemap.nodes[1]['ville'] = 'lyon'
        simple_edge = gr_simplemap.to_geopandas_edgelist()
        simple_node = gr_simplemap.to_geopandas_nodelist()
        gr_simplemap2 = gnx.from_geopandas_edgelist(simple_edge, node_attr=True, node_gdf=simple_node, node_id='node_id')
        self.assertTrue(graphs_equal(gr_simplemap, gr_simplemap2))

class TestUtils(unittest.TestCase):
    """tests utils module"""

    def test_cast(self):
        """tests cast function"""
        tests = [ 1, '01', [1,2], [1, '02']]
        tests2 = [ 'x1', [1, 'x2']]
        tests3 = [None, [1, None]]
        for test in tests:
            self.assertTrue(utils.cast_id(test) in (1, [1,2]))
            self.assertEqual(utils.cast_id(test, True), utils.cast_id(test))
        for test in tests2:
            self.assertEqual(utils.cast_id(test), test)
            self.assertTrue(utils.cast_id(test, True) in (None, [1]))
        for test in tests3:
            self.assertTrue(utils.cast_id(test, True) in (None, [1]))
            self.assertTrue(utils.cast_id(test, True) in (None, [1]))

    def test_geo_merge(self):
        """ test geo_merge function"""
        l1 = LineString([(0,0), (1,1), (2,2)])            
        l1r = LineString([(2,2), (1,1), (0,0)])     
        l1s = LineString([(3,3), (4,4), (5,5)])    
        l1jr = LineString([(0,0), (6,6)])            
        l1j = LineString([(-1,-1), (0,0)])            
        l1c = LineString([(0, 2), (2, 0)])    
        pt1 = Point((1.5, 1.5))
        pt1e = Point((1.5, 2.5))
        self.assertTrue(utils.geo_merge(l1, l1r) is not None)
        self.assertTrue(utils.geo_merge(l1j, l1c) is not None)
        self.assertTrue(utils.geo_merge(l1s, l1jr) is None)
        self.assertTrue(utils.geo_merge(l1s, l1j, False) is None)
        self.assertEqual(utils.geo_merge(pt1, pt1), pt1)
        self.assertEqual(utils.geo_merge(l1, l1s), utils.geo_merge(l1r, l1s))
        self.assertEqual(utils.geo_merge(l1, pt1), l1)
        self.assertEqual(utils.geo_merge(pt1e, pt1), LineString([pt1, pt1e]))
        self.assertTrue(utils.geo_merge(pt1e, pt1, False) is None)

if __name__ == "__main__":
    unittest.main(verbosity=2)
