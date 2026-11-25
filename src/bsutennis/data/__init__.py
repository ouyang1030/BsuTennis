"""
Data: the standard tables, loaders for open data, and the local cache.

    from bsutennis.data import load_slam
    wimbledon = load_slam(2023, "wimbledon")
    wimbledon.points.groupby("server").server_won.mean()
"""

from .dataset import Dataset
from .schema import MATCH_COLUMNS, PLAYER_COLUMNS, POINT_COLUMNS, SHOT_COLUMNS
from .sources.mcp import load_charting
from .sources.results import load_results
from .sources.slam_pbp import load_slam

__all__ = [
    "Dataset",
    "MATCH_COLUMNS",
    "PLAYER_COLUMNS",
    "POINT_COLUMNS",
    "SHOT_COLUMNS",
    "load_charting",
    "load_results",
    "load_slam",
]
