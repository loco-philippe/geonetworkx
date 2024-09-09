geonetworkx.geograph
====================

.. py:module:: geonetworkx.geograph

.. autoapi-nested-parse::

   This module contains the `GeoGraph` class.



Exceptions
----------

.. autoapisummary::

   geonetworkx.geograph.GeoGraphError


Classes
-------

.. autoapisummary::

   geonetworkx.geograph.GeoGraph


Module Contents
---------------

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



.. py:exception:: GeoGraphError

   Bases: :py:obj:`Exception`


   GeoGraph Exception


