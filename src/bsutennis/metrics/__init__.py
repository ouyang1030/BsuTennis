"""
Metrics: numbers computed from the standard tables.

Works on any :class:`~bsutennis.data.Dataset` through its column names alone:
serve / return percentages, serves and their predictability, the value of
every stroke, win probability of every point, Elo ratings.
"""

from .ratings import elo
from .serve_return import serve_return
from .serves import serve_entropy, serves
from .shot_value import shot_values
from .win_probability import point_probabilities, serve_shares

__all__ = ["serve_return", "serves", "serve_entropy", "shot_values", "serve_shares", "point_probabilities", "elo"]
