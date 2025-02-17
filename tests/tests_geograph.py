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

class TestGeoDiGraph(unittest.TestCase):
    """tests GeoDiGraph class"""

    def test_empty_geodigraph(self):
        """tests empty GeoDiGraph"""
        dgr = gnx.GeoDiGraph(crs=2154)
        self.assertEqual(len(dgr), 0)

    def test_geodigraph(self):
        """tests GeoDiGraph"""
        simplemap = gpd.GeoDataFrame({'geometry': [LineString([paris, lyon]), LineString([lyon, marseille]), 
            LineString([paris, bordeaux]), LineString([bordeaux, marseille])]}, crs=4326).to_crs(2154)
        gr_simple = gnx.from_geopandas_edgelist(simplemap)
        gr_simple.nodes[0]['city'] = 'paris'
        gr_simple.nodes[1]['ville'] = 'lyon'
        dgr_simple = gr_simple.to_directed()
        self.assertTrue(len(dgr_simple.nodes) == len(dgr_simple.nodes) == len(simplemap))
        dgr_simple_edges = dgr_simple.to_geopandas_edgelist()
        gr_edges = gr_simple.to_geopandas_edgelist()
        dgr_edges = dgr_simple_edges.iloc[[0,1,3,5]].reset_index(drop=True)
        self.assertTrue(gr_edges.equals(dgr_edges))
        dgr_simple_nodes = dgr_simple.to_geopandas_nodelist()
        gr_nodes = gr_simple.to_geopandas_nodelist()
        self.assertTrue(gr_nodes.equals(dgr_simple_nodes))
        
class TestGeoGraph(unittest.TestCase):
    """tests GeoGraph class"""

    def test_empty_geograph(self):
        """tests empty GeoGraph"""
        gr = gnx.GeoGraph(crs=2154)
        self.assertEqual(len(gr), 0)
        
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

    def test_erase_linear_nodes(self):
        """test erase_linear_nodes method"""
        simplemap = gpd.GeoDataFrame({'geometry': [LineString([paris, lyon]), LineString([lyon, marseille]), 
            LineString([paris, bordeaux]), LineString([lyon, bordeaux]), LineString([bordeaux, marseille])]}, crs=4326).to_crs(2154)
        gr = gnx.from_geopandas_edgelist(simplemap)
        len_gr = (len(gr.nodes), len(gr.edges))
        res = gr.erase_linear_nodes(2)
        self.assertEqual((len(gr.nodes), len(gr.edges)), len_gr)
        self.assertFalse(res)
        res = gr.erase_linear_nodes(3)
        self.assertEqual((len(gr.nodes), len(gr.edges)), len_gr)
        self.assertFalse(res)
        gr.remove_edge(1,2)
        gr.add_edges_from([(0,1,{'a':1, 'b':2}), (1,3,{'a':2, 'c':4})])
        weight = gr.edges[0,1]['weight'] + gr.edges[1,3]['weight']
        res = gr.erase_linear_nodes(1)
        self.assertEqual(gr.edges[0,3]['a'], 2)
        self.assertEqual(gr.edges[0,3]['b'], 2)
        self.assertEqual(gr.edges[0,3]['c'], 4)
        self.assertEqual(gr.edges[0,3]['weight'], weight)
        self.assertEqual((len(gr.nodes), len(gr.edges)), (len_gr[0]-1, len_gr[1]-2))
        self.assertTrue(res)

    def test_erase_all_linear_nodes(self):
        """test erase_linear_nodes method"""
        simplemap = gpd.GeoDataFrame({'geometry': [LineString([paris, lyon]), LineString([lyon, marseille]), 
            LineString([paris, bordeaux]), LineString([lyon, bordeaux]), LineString([bordeaux, marseille])]}, crs=4326).to_crs(2154)
        gr = gnx.from_geopandas_edgelist(simplemap)
        len_gr = (len(gr.nodes), len(gr.edges))
        res = gr.erase_linear_nodes()
        self.assertEqual((len(gr.nodes), len(gr.edges)), len_gr)
        self.assertFalse(res)
        gr.remove_edge(1,2)
        res = gr.erase_linear_nodes()
        self.assertEqual((len(gr.nodes), len(gr.edges)), (len_gr[0]-1, len_gr[1]-2))
        self.assertTrue(res)
        
class Test_geopandas_nodelist(unittest.TestCase):
    """tests GeoPandas convertion"""

    def test_node_id(self):
        """test 'node_id' attribute"""
        node_gdf = gpd.GeoDataFrame({'geometry': [paris, lyon, marseille, bordeaux], 
                                     'node_id': [10, 20, 30, 40], 
                                     'nature': ['ville', 'ville', 'ville', 'ville']}, crs=4326).to_crs(2154) 
        gs_noeuds = gnx.from_geopandas_nodelist(node_gdf, node_id='node_id', node_attr=True)
        node_gdf2 = gs_noeuds.to_geopandas_nodelist()
        gs_noeuds2 = gnx.from_geopandas_nodelist(node_gdf2, node_id='node_id', node_attr=True)
        self.assertTrue(graphs_equal(gs_noeuds, gs_noeuds2))
        
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
