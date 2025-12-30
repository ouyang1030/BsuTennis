"""
BsuTennis
~~~~~~~~~
Tennis analytics and visualization library for sports data science.

Provides tools for:
- Court visualization (TennisCourt)
- Shot distribution analysis (KDE, heatmaps, hexbin)
- Statistical charts (pizza, radar, sonar)
- Joint plots with marginal distributions

Full documentation: https://github.com/ouyang1030/tennis
:copyright: (c) 2025 by SIG BSU.
:license: MIT, see LICENSE for more details.
"""

__version__ = "1.0.0"

# =============================================================================
# Core Court Visualization
# =============================================================================
from .pitch import TennisCourt
from .theme import THEMES, SCATTER_STYLES
from .grid import create_court_grid

# =============================================================================
# Advanced Visualizations
# =============================================================================
from .joint import joint_plot
from .pizza import pizza_chart, pizza
from .sonar import sonar_chart, sonar_from_shots, create_zone_grid
from .radar import Radar

# =============================================================================
# Statistical Charts
# =============================================================================
from .chart import (
    plot_bar,
    plot_bar_comparison,
    plot_horizontal_bar,
    plot_line,
    plot_pie,
    plot_table
)

# =============================================================================
# Data Processing & Statistics
# =============================================================================
from .stats import transform_coordinate, classify_serve_zone, classify_shot_depth

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    # Core
    'TennisCourt',
    'THEMES',
    'SCATTER_STYLES',
    'create_court_grid',
    
    # Advanced Viz
    'joint_plot',
    'pizza_chart',
    'pizza',
    'sonar_chart',
    'sonar_from_shots',
    'create_zone_grid',
    'Radar',
    
    # Charts
    'plot_bar',
    'plot_bar_comparison',
    'plot_horizontal_bar',
    'plot_line',
    'plot_pie',
    'plot_table',
    
    # Stats
    'transform_coordinate',
    'classify_serve_zone',
    'classify_shot_depth',
]
