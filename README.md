# Geo-NX : Geospatial Network Analysis <img src="./docs/geo_nx.png" alt="geo_nx" style="float:right;width:100px;height:90px;">

Geo-NX is a Python package for the creation, manipulation, and study of geospatial networks.

Geo-NX extends NetworkX operations to allow operations on geometric types.

*The Geo-NX package was created as part of the [Qualicharge](https://github.com/MTES-MCT/qualicharge) project*

## Description

Geo-NX combines the capabilities of NetworkX, GeoPandas and shapely :

- NetworkX is the core of Geo-NX,
- GeoPandas is the support for vectorized processing,
- Geo-NX uses shapely for geometry analysis and manipulation  

Documentation is available at https://loco-labs.github.io/geo_nx/

## Data structures

`geo_nx.GeoGraph` is a subclass of `networkx.Graph` with additional data:

- 'crs': coordinate reference system,
- 'geometry': geospatial representation of nodes and edges.

A `geo_nx.GeoGraph` has two representations:

- a `networkx.Graph` representation where 'crs' is a graph attribute and 'geometry' 
is a node and edge attribute (shapely object),
- a `geopandas.GeoDataFrame` representation for the nodes and for the edges where columns are id (node or edge) and attributes.

## Example

Simple distance from Paris to Marseille

```python
In [1]: import geo_nx as gnx
        
        paris = Point(2.3514, 48.8575)
        lyon = Point(4.8357, 45.7640)
        marseille = Point(5.3691, 43.3026)
        bordeaux = Point(-0.56667, 44.833328)

In [2]: simplemap = gpd.GeoDataFrame({
            'geometry': [
                LineString([paris, lyon]), 
                LineString([lyon, marseille]), 
                LineString([paris, bordeaux]), 
                LineString([bordeaux, marseille])
            ]}, crs=4326).to_crs(2154)

In [3]: gr_simplemap = gnx.from_geopandas_edgelist(simplemap)

In [4]: gr_simplemap.to_geopandas_nodelist()
Out[4]:
                             geometry    node_id
    0  POINT (652411.148 6862135.813)          0
    1  POINT (842666.659 6519924.367)          1
    2  POINT (892313.068 6247711.351)          3
    3  POINT (418208.312 6421272.355)          2

In [5]: # 0: paris, 1: lyon, 2: bordeaux, 3: marseille
        # weight is a calculated attribute (length of a geometry)
        nx.shortest_path(gr_simplemap, source=0, target=3, weight='weight')
Out[5]: [0, 1, 3]

In [6]: nx.shortest_path_length(gr_simplemap, source=0, target=3, weight='weight')
Out[6]: 668246.1446978811
```

## Install

Install the latest released version of Geo-NX:

```shell
pip install geo_nx
```

## Bugs

Please report any bugs that you find [here](https://github.com/loco-labs/geo_nx/issues). 
Or, even better, fork the repository on GitHub and create a pull request (PR).