# -*- coding: utf-8 -*-
"""
`geo_nx` setup
"""

import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="geo_nx",
    version="0.3.0",
    description="Geo-NX : Geospatial Network Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loco-labs/geo_nx/blob/main/README.md",
    author="Philippe Thomy",
    author_email="philippe@loco-labs.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="network, geographic, geospatial, open data",
    packages=find_packages(include=["geo_nx", "geo_nx.*"]),
    python_requires=">=3.11, <4",
    install_requires=["shapely", "geopandas"]
)
