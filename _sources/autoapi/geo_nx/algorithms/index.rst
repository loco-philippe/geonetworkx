geo_nx.algorithms
=================

.. py:module:: geo_nx.algorithms

.. autoapi-nested-parse::

   Operations on graphs.



Functions
---------

.. autoapisummary::

   geo_nx.algorithms.compose


Module Contents
---------------

.. py:function:: compose(geo_g, geo_h)

   Compose GeoGraph geo_g with geo_h by combining nodes and edges into a single graph.

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


