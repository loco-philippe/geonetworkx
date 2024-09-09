geonetworkx.convert
===================

.. py:module:: geonetworkx.convert

.. autoapi-nested-parse::

   This module contains conversion functions between `geonetworkx.GeoGraph` data and
   `geopandas.GeoDataFrame` data.

   The conversion follows two principles:

   - reversibility: A round-trip return the initial object (lossless conversion),
   - optimization: Missing geometries ares reconstructed in two cases. If the nodes are not
     present, nodes are added with a geometry corresponding to edges ends. If
     the geometries edges are not present, a segment between the nodes geometry is added.



Attributes
----------

.. autoapisummary::

   geonetworkx.convert.GEOM
   geonetworkx.convert.WEIGHT


Functions
---------

.. autoapisummary::

   geonetworkx.convert.from_geopandas_nodelist
   geonetworkx.convert.from_geopandas_edgelist
   geonetworkx.convert.to_geopandas_edgelist
   geonetworkx.convert.to_geopandas_nodelist


Module Contents
---------------

.. py:data:: GEOM
   :value: 'geometry'


.. py:data:: WEIGHT
   :value: 'weight'


.. py:function:: from_geopandas_nodelist(node_gdf, node_id=None, node_attr=None)

   Convert a GeoDataFrame in an empty GeoGraph (without edges).

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


.. py:function:: from_geopandas_edgelist(edge_gdf, source='source', target='target', edge_attr=None, node_gdf=None, node_id=None, node_attr=None)

   Returns a GeoGraph from GeoDataFrame containing an edge list.

   The GeoDataFrame should contain at least three columns (node id source, node id target,
   geometry).
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
       GeoGraph with edges of the GeoDataFrame.


.. py:function:: to_geopandas_edgelist(graph, source='source', target='target', nodelist=None)

   Returns the graph edge list as a GeoDataFrame.

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


.. py:function:: to_geopandas_nodelist(graph, node_id='node_id', nodelist=None)

   Returns the graph node list as a GeoDataFrame.

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


