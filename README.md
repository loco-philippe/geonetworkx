# GeoNetworkX : Geospatial Network Analysis


GeoNetworkX is a Python package for the creation, manipulation, and study of geospatial networks.

GeoNetworkX extends NetworkX operations to allow spatial operations on geometric types.

## Description

GeoNetworkX combines the capabilities of NetworkX, GeoPandas and shapely :

- Networkx is the core of GeoNetworkX,
- GeoPandas is the support for vectorized processing,
- GeoNetworkX uses shapely for geometry analysis and manipulation  


## Data structures

geonetworkx.GeoGraph is a subclass of networkx.Graph with additional data:

- 'crs': coordinate reference system,
- 'geometry': geospatial representation of nodes and edges.

A geonetworkx.GeoGraph has two representations:

- a networkx.Graph representation where 'crs' is a graph attribute and 'geometry' 
is a node and edge attribute (shapely object),
- a geopandas.GeoDataFrame representation for the nodes and for the edges 

## Install



## Example

Distance from Paris to Marseille

```python
paris = Point(2.3514, 48.8575)
lyon = Point(4.8357, 45.7640)
marseille = Point(5.3691, 43.3026)
bordeaux = Point(-0.56667, 44.833328)

simplemap = gpd.GeoDataFrame({
    'geometry': [
        LineString([paris, lyon]), 
        LineString([lyon, marseille]), 
        LineString([paris, bordeaux]), 
        LineString([bordeaux, marseille])
    ]}, crs=4326).to_crs(2154)

gr_simplemap = gnx.from_geopandas_edgelist(simplemap)

gr_simplemap.to_geopandas_nodelist()

                             geometry    node_id
    0  POINT (652411.148 6862135.813)          0
    1  POINT (842666.659 6519924.367)          1
    2  POINT (892313.068 6247711.351)          3
    3  POINT (418208.312 6421272.355)          2

# 0: paris, 1: lyon, 2: bodeaux, 3: marseille
nx.shortest_path(gr_simplemap, source=0, target=3, weight='weight')
    [0, 1, 3]

nx.shortest_path_length(gr_simplemap, source=0, target=3, weight='weight')
    668246.1446978811
```
