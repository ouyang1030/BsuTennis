"""
Rules of tennis: match formats and the scoring state machine.

Pure Python; no pandas, numpy or matplotlib.
"""

from .formats import (
    ADVANTAGE_SET,
    MATCH_TIEBREAK,
    TEN_POINT_TIEBREAK_SET,
    MatchFormat,
    SetFormat,
    grand_slam,
    grand_slam_final_set,
)
from .score import Score, replay

__all__ = [
    "SetFormat",
    "MatchFormat",
    "ADVANTAGE_SET",
    "MATCH_TIEBREAK",
    "TEN_POINT_TIEBREAK_SET",
    "grand_slam",
    "grand_slam_final_set",
    "Score",
    "replay",
]
