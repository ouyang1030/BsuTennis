"""
bsutennis
~~~~~~~~~
Tennis data processing, analysis and visualisation.

Subpackages, lowest layer first (each depends only on the ones above it)
------------------------------------------------------------------------
geometry
    Court dimensions, the standard coordinate frame, zone classification.
rules
    Match formats and the scoring state machine.
data
    The standard ``matches`` / ``players`` / ``points`` / ``shots`` tables and loaders for open data.
models
    Probability models: win probability and point importance from serve
    strengths; the Elo rating update.
metrics
    Numbers computed from the standard tables: serve / return percentages,
    win probability of every point, Elo ratings.
viz
    Court plots (scatter, KDE, heatmap, hexbin, arrows), pizza, radar,
    sonar, joint plots and simple statistical charts.

The most common names are re-exported here, e.g.::

    from bsutennis import TennisCourt, load_slam

Documentation: https://github.com/ouyang1030/BsuTennis

:copyright: (c) 2025 Jiangyan Yang.
:license: MIT, see LICENSE for details.
"""

__version__ = "0.1.0"

from . import data, geometry, metrics, models, rules, viz
from .data import Dataset, load_charting, load_results, load_slam
from .geometry import classify_serve_zone, classify_shot_depth, transform_coordinate
from .viz import (
    SCATTER_STYLES,
    THEMES,
    Radar,
    TennisCourt,
    create_court_grid,
    create_zone_grid,
    joint_plot,
    pizza,
    pizza_chart,
    plot_bar,
    plot_bar_comparison,
    plot_horizontal_bar,
    plot_line,
    plot_pie,
    plot_table,
    sonar_chart,
    sonar_from_shots,
)

__all__ = [
    # data
    "Dataset",
    "load_charting",
    "load_results",
    "load_slam",
    # geometry
    "transform_coordinate",
    "classify_serve_zone",
    "classify_shot_depth",
    # viz
    "TennisCourt",
    "THEMES",
    "SCATTER_STYLES",
    "create_court_grid",
    "joint_plot",
    "pizza_chart",
    "pizza",
    "sonar_chart",
    "sonar_from_shots",
    "create_zone_grid",
    "Radar",
    "plot_bar",
    "plot_bar_comparison",
    "plot_horizontal_bar",
    "plot_line",
    "plot_pie",
    "plot_table",
]
