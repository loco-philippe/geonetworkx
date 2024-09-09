geonetworkx
===========

.. py:module:: geonetworkx

.. autoapi-nested-parse::

   **GeoNetworkX Package**

   This package contains classes and functions for geospatial networks.

   For more information, see the
   [github repository](https://github.com/loco-labs/geonetworks).



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/geonetworkx/algorithms/index
   /autoapi/geonetworkx/convert/index
   /autoapi/geonetworkx/geograph/index
   /autoapi/geonetworkx/utils/index


Classes
-------

.. autoapisummary::

   geonetworkx.GeoGraph


Functions
---------

.. autoapisummary::

   geonetworkx.from_geopandas_edgelist
   geonetworkx.from_geopandas_nodelist
   geonetworkx.to_geopandas_edgelist
   geonetworkx.to_geopandas_nodelist
   geonetworkx.compose
   geonetworkx.geom_to_crs
   geonetworkx.cast_id


Package Contents
----------------

.. py:class:: GeoGraph(incoming_graph_data=None, **attr)

   Bases: :py:obj:`networkx.Graph`


   This class analyses geospatial graphs.

   A geospatial graph is a graph where nodes and edges are related to a geometry.

   A GeoGraph is a NetworkX Graph with a shapely geometry as egde attribute and node attribute.

   The GeoGraph 'crs' attribute defines the coordinate reference used.

   *instance methods*

   - `insert_node`
   - `to_geopandas_edgelist`
   - `to_geopandas_nodelist`
   - `plot`
   - `explore`
   - `find_nearest_edge`
   - `find_nearest_node`



   .. py:method:: insert_node(geom, id_node, id_edge, att_node={}, adjust=False)

      Cut an edge in two edges and insert a new node between each.

      The 'geometry' attribute of the two edges and the new node is build from the geometry of
      the initial edge and the parameter geometry.

      Parameters
      ----------

      id_node: id
          Id of the inserted node.
      att_node: dict
          Attributes of the inserted node.
      id_edge: tuple of two id_node
          Id of the cuted edge.
      geom: shapely geometry
          Geometry to be projected on the edge line (centroid projection).
      adjust: boolean
          If True, the new point is the geometry's centroid else the projected line point

      Returns
      -------

      dist: float
          Abcissa of the new node in the cuted edge geometry.

      Note
      ----

      This method is available only with LineString as edge geometry.



   .. py:method:: to_geopandas_edgelist(source='source', target='target', nodelist=None)

      see `convert.to_geopandas_edgelist`



   .. py:method:: to_geopandas_nodelist(node_id='node_id', nodelist=None)

      see `convert.to_geopandas_nodelist`



   .. py:method:: plot(edges=True, nodes=True, **param)

      Plot a GeoGraph.

      Generate a plot of the edges GeoDataFrame and nodes GeoDataFrame with matplotlib.

      Parameters
      ----------

      edges: boolean - default True
          If True, edges are included in the plot.
      nodes: boolean - default True
          If True, nodes are included in the plot.
      param: dict
          `GeoDataFrame.plot` parameters. Parameters are common to edges and nodes.
          Specific parameters to nodes or edges are preceded by *n_* or *e_* (eg 'e_color').
          Default is {'e_edgecolor': 'black', 'n_marker': 'o', 'n_color': 'red',
          'n_markersize': 5}



   .. py:method:: explore(refmap=None, edges=True, nodes=True, nodelist=None, layercontrol=False, **param)

      Interactive map based on GeoPandas and folium/leaflet.js

      Generate an interactive leaflet map based on the edges GeoDataFrame and nodes GeoDataFrame.

      Parameters
      ----------

      refmap: dict or folium map - default None
          Existing map instance or map defined by a dict (see folium Map keywords)
          on which to draw the GeoGraph.
      edges: boolean
          If True, edges are includes in the plot.
      nodes: boolean
          If True, nodes defined by nodelist are included in the plot.
      nodelist: list - default None
          Use only nodes specified in nodelist (all if None).
      layercontrol: boolean - default False
          Add folium.LayerControl to the map if True.
      param: dict
          `GeoDataFrame.explore` parameters. Parameters are common to edges and nodes.
          Specific parameters to nodes or edges are preceded by *n_* or *e_* (eg 'e_color')



   .. py:method:: find_nearest_edge(geom, max_distance)

      Find the closest edge to a geometry

      Spatial join based on the distance between given geometry and edges geometries.

      Results will include a single output records (even in case of multiple 
      nearest and equidistant geometries).

      Parameters
      ----------
      geom : Shapely Geometry
          Geometry used in the spatial join.
      max_distance : float
          Maximum distance within which to query for nearest geometry.

      Returns
      -------
      list
          id of the nearest edge (list of two id_node)



   .. py:method:: find_nearest_node(geom, max_distance)

      Find the closest node to a geometry.

      Spatial join based on the distance between given geometry and nodes geometries.

      Results will include a single output records (even in case of multiple 
      nearest and equidistant geometries).

      Parameters
      ----------
      geom : Shapely Geometry
          Geometry used in the spatial join.
      max_distance : float
          Maximum distance within which to query for nearest geometry.

      Returns
      -------
      list
          id of the nearest edge (list of two id_node)



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


.. py:function:: geom_to_crs(geom, crs, new_crs)

   convert geometry coordinates from a CRS to another CRS

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


.. py:function:: cast_id(node_id, only_int=False)

   replace number string as integer in a single or an iterable.

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


