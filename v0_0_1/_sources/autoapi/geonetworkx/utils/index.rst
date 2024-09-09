geonetworkx.utils
=================

.. py:module:: geonetworkx.utils

.. autoapi-nested-parse::

   Functions used for geometry analysis



Attributes
----------

.. autoapisummary::

   geonetworkx.utils.GEOM
   geonetworkx.utils.WEIGHT


Functions
---------

.. autoapisummary::

   geonetworkx.utils.geo_cut
   geonetworkx.utils.nodes_gdf_from_edges_gdf
   geonetworkx.utils.add_geometry_edges_from_nodes
   geonetworkx.utils.geom_to_crs
   geonetworkx.utils.cast_id


Module Contents
---------------

.. py:data:: GEOM
   :value: 'geometry'


.. py:data:: WEIGHT
   :value: 'weight'


.. py:function:: geo_cut(line, geom, adjust=False)

   Cuts a line in two at the geometry nearest projection point

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


.. py:function:: nodes_gdf_from_edges_gdf(e_gdf, source=None, target=None)

   create a nodes GeoDataFrame from an edges GeoDataFrame.

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


.. py:function:: add_geometry_edges_from_nodes(e_gdf, source, target, n_gdf, node_id)

   add a geometry column in an edges GeoDataFrame from geometry nodes.

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


