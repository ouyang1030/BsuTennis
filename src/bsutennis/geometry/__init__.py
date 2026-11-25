"""
Court geometry: dimensions, coordinate systems and zones.

numpy and pandas only; nothing here imports matplotlib.
"""

from . import dimensions
from .coords import transform_coordinate
from .court import BaseCourt
from .zones import (
    RALLY_LANES,
    RETURN_DEPTHS,
    RETURN_ZONES,
    Zone,
    classify_serve_zone,
    classify_shot_depth,
    serve_zones,
)

__all__ = [
    "dimensions",
    "BaseCourt",
    "transform_coordinate",
    "classify_serve_zone",
    "classify_shot_depth",
    "Zone",
    "serve_zones",
    "RALLY_LANES",
    "RETURN_DEPTHS",
    "RETURN_ZONES",
]
