"""
Climate Scenario Pipeline Package

This package provides tools for processing and analyzing climate scenario data.
"""

__version__ = "1.0.0"
__author__ = "Research & Emerging Topics in Data Science"

from . import config
from . import io
from . import processing
from . import scenarios
from . import visualization
from . import utils

__all__ = [
    'config',
    'io',
    'processing',
    'scenarios',
    'visualization',
    'utils'
]
