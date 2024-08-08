# -*- coding: utf-8 -*-
"""
`geonetworkx` setup
"""

import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="geonetworkx",
    version="0.0.1",
    description="Geo-NetworkX : A tool to analyse geographic network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loco-philippe/geonetworkx/blob/main/README.md",
    author="Philippe Thomy",
    author_email="philippe@loco-labs.io",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="network, geographic, open data",
    packages=find_packages(include=["geonetworkx", "geonetworkx.*"]),
    python_requires=">=3.11, <4",
    install_requires=[],
)
