# -*- coding: utf-8 -*-
"""
This module contains the `GeoGraph` class.
"""

import shapely
from shapely import LineString, Point
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import networkx as nx
import matplotlib.pyplot as plt


class GeoGraph(nx.Graph):
    """This class analyses geographic graphs.

    *Attributes*

    - **crs** : string or integer - Coordinate Reference System used

    *characteristic (@property)*

    - `iscomplete`
    - `ratecodec`
    - `dmincodec`
    - `dmaxcodec`
    - `rancodec`
    - `typecodec`

    *instance methods*

    - `to_dict`

    """

    def __init__(self, crs, incoming_graph_data=None, **attr):
        """Creation mode :

        *Parameters (multiple attributes)*

        - **idfield** : string or integer - Id of the Field

        *example*

        AnaField is created with a dict
        >>> AnaField(Cfield([1,2,3,3]).to_analysis).to_dict()
        {'lencodec': 4, 'mincodec': 3, 'maxcodec': 4}
        >>> AnaField({'lencodec': 4, 'mincodec': 3, 'maxcodec': 4})
        {'lencodec': 4, 'mincodec': 3, 'maxcodec': 4}

        AnaField is created with parameters
        >>> AnaField(lencodec=4, mincodec=3, maxcodec=4).to_dict()
        {'lencodec': 4, 'mincodec': 3, 'maxcodec': 4}
        >>> AnaField(4, 3, 4).to_dict()
        {'lencodec': 4, 'mincodec': 3, 'maxcodec': 4}
        """
        attr = attr | {'crs': crs}
        super().__init__(incoming_graph_data, **attr)
        


class GeoGraphError(Exception):
    """GeoGraph Exception"""
