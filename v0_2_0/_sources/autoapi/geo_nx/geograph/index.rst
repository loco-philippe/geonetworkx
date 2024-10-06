geo_nx.geograph
===============

.. py:module:: geo_nx.geograph

.. autoapi-nested-parse::

   This module contains the `GeoGraph` class.



Attributes
----------

.. autoapisummary::

   geo_nx.geograph.GEOM
   geo_nx.geograph.WEIGHT
   geo_nx.geograph.NODE_ID


Exceptions
----------

.. autoapisummary::

   geo_nx.geograph.GeoGraphError


Classes
-------

.. autoapisummary::

   geo_nx.geograph.GeoGraph


Module Contents
---------------

.. py:data:: GEOM
   :value: 'geometry'


.. py:data:: WEIGHT
   :value: 'weight'


.. py:data:: NODE_ID
   :value: 'node_id'


.. py:class:: GeoGraph(incoming_graph_data=None, **attr)

   Bases: :py:obj:`networkx.Graph`


   This class analyses geospatial graphs.

   A geospatial graph is a graph where nodes and edges are related to a geometry.

   A GeoGraph is a NetworkX Graph with a shapely geometry as egde attribute and node attribute.

   The GeoGraph 'crs' attribute defines the coordinate reference used.

   *instance methods*

   - `insert_node`
   - `project_node`
   - `to_geopandas_edgelist`
   - `to_geopandas_nodelist`
   - `plot`
   - `explore`
   - `find_nearest_edge`
   - `find_nearest_node`
   - `weight_extend`



   .. py:method:: merge_node(add_node, graph, radius)

      Find the nearest node of 'graph' and update attr

      Parameters
      ----------

      add_node: id
          Id of the node to project.
      graph: GeoGraph
          Graph to connect to the add_node.
      radius : float
          Maximum distance between add_node and graph.

      Returns
      -------

      dist: float
          Distance between add_node and graph (None if distance > radius).
        



   .. py:method:: project_node(add_node, graph, radius, att_edge=None, update_node=False, target_node=None)

      Add an external node in a Graph.

      Update the nearest node of 'graph' or
      add a LineString edge between 'add_node' and the nearest node of 'graph'.
      The LineString length has to be lower than radius.

      Parameters
      ----------

      add_node: id
          Id of the node to project.
      target_node: id
          Id of the graph node to project add_node. If None, the nearest is used.
      att_edge: dict
          Attributes of the added edge.
      graph: GeoGraph
          Graph to connect to the add_node.
      radius: float
          Maximum distance between add_node and graph.
      update_node: boolean
          If True, the nearest node is updated with 'add_node' attributes.
          If False, a LineString edge is added.

      Returns
      -------

      dist: float
          Distance between add_node and graph (None if distance > radius).
        



   .. py:method:: erase_node(id_node, adjust=False)

      to be define



   .. py:method:: insert_node(geom, id_node, id_edge, att_node=None, adjust=False)

      Cut an edge in two edges and insert a new node between each.

      The 'geometry' attribute of the two edges and the new node is build from the geometry of
      the initial edge and the parameter geometry.

      Parameters
      ----------

      id_node: id
          Id of the inserted node.
      att_node: dict (default None)
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



   .. py:method:: weight_extend(edge, ext_gr, radius=None, n_attribute=None, n_active=None)

      Find the path (witch contains edge) between nodes included in 
      a projected graph and with minimal weight.

      Parameters
      ----------
      edge : tuple
          Edge to extend in the projected graph.
      ext_gr : Graph
          Projected Graph.
      radius : float (default None)
          radius used to find the nearest external node for each node of the edge.
          If None, the radius used is the weight of the edge.
      n_attribute : str (default None)
          Node attribute to store node projected distance.
      n_active : str (default None)
          Node attribute that indicates the validity (boolean) of the node.
      Returns
      -------
      float
          extended weight



   .. py:method:: weight_node_to_graph(node, ext_gr, radius=None, attribute=None, active=None)

      Return the distance between a node and a projected graph.

      Parameters
      ----------
      node : int or str
          Origin of the distance measure.
      ext_gr : Graph
          Projected Graph
      radius : float (default None)
          value used to filter projected nodes before analyse.
          If None, all the projected graph is used.
      attribute : int or str (default None)
          Node attribute to store resulted distance
      active : str (default None)
          ext_gr node attribute that indicates the validity (boolean) of the node.
      Returns
      -------
      float
          distance between the node and the projected graph



.. py:exception:: GeoGraphError

   Bases: :py:obj:`Exception`


   GeoGraph Exception


