# -*- coding: utf-8 -*-
"""
===========================================
Benchpress: a benchmark tool and collection
===========================================

Benchpress is primarily a tool for running benchmarks and analyze/visualize the result.

The workflow:
    - Write a Python program that generates the commands to run and write the commands to a JSON file
    - Use `bp-run` to *run* the JSON file
    - Use a visualizer such as `bp-cli` or `bp-chart` to visualize the results within the JSON file

"""
from pkg_resources import get_distribution, DistributionNotFound
import util
import visualizer
import suite_util
from .benchpress import *

# Set the package version
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
