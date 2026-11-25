"""
Sonar Chart Visualization for Tennis Analytics.

Creates directional distribution charts overlaid on court zones,
showing where shots go from each zone (or where incoming shots come from).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Wedge, Circle
from matplotlib.collections import PatchCollection
import numpy as np


def sonar_chart(ax, zone_data, court=None, 
                n_directions=6,
                zone_size=1.8,
                cmap='bsu',
                alpha=0.85,
                show_labels=True,
                center_color='#1a1a2e',
                edge_color='white',
                direction_labels=None,
                **kwargs):
    """
    Create a sonar chart showing shot direction distributions from court zones.
    
    Parameters
    ----------
    ax : matplotlib axes
        The axes to draw on (should already have court drawn).
    zone_data : list of dict
        Each dict contains:
        - 'x', 'y': Zone center coordinates (in court coords)
        - 'directions': list of values (counts or percentages) for each direction
        Example: [{'x': 0, 'y': 5, 'directions': [15, 25, 30, 10, 12, 8]}, ...]
    court : TennisCourt, optional
        Court object for coordinate transformation.
    n_directions : int, default 6
        Number of direction segments (wedges).
    zone_size : float, default 1.8
        Radius of each sonar chart in court units.
    cmap : str, default 'bsu'
        Color scheme: 'bsu', 'heat', 'cool'.
    alpha : float, default 0.85
        Transparency of wedges.
    show_labels : bool, default True
        Show percentage labels on wedges.
    center_color : str
        Color of center circle.
    edge_color : str
        Edge color of wedges.
    direction_labels : list of str, optional
        Custom labels for directions (e.g., ['Cross', 'DTL', ...]).
    
    Returns
    -------
    collections : list of PatchCollection
    """
    
    # Color schemes
    color_schemes = {
        'bsu': ['#92e3da', '#5bc0be', '#3a86ff', '#8338ec', '#ff006e', '#fb5607', '#ffbe0b', '#06d6a0'],
        'heat': ['#ff0000', '#ff4400', '#ff8800', '#ffcc00', '#ffff00', '#ccff00', '#88ff00', '#44ff00'],
        'cool': ['#3498db', '#2980b9', '#9b59b6', '#8e44ad', '#1abc9c', '#16a085', '#e74c3c', '#c0392b'],
    }
    
    colors = color_schemes.get(cmap, color_schemes['bsu'])
    
    # Ensure we have enough colors
    while len(colors) < n_directions:
        colors = colors + colors
    colors = colors[:n_directions]
    
    all_patches = []
    
    for zone in zone_data:
        cx, cy = zone['x'], zone['y']
        directions = zone['directions']
        
        # Handle coordinate transformation for horizontal courts
        if court and court.orientation == 'horizontal':
            plot_x, plot_y = cy, cx
        else:
            plot_x, plot_y = cx, cy
        
        # Normalize directions to get radii (max = zone_size)
        directions = np.array(directions)
        if directions.max() > 0:
            norm_dirs = directions / directions.max()
        else:
            norm_dirs = directions
        
        # Calculate percentages for labels
        total = directions.sum()
        percentages = (directions / total * 100) if total > 0 else directions
        
        # Create wedges for each direction
        angle_step = 360 / n_directions
        patches = []
        
        for i in range(n_directions):
            # Start angle (0 = up/forward)
            theta1 = 90 - (i * angle_step) - angle_step / 2
            theta2 = 90 - (i * angle_step) + angle_step / 2
            
            # Radius based on value
            r = zone_size * (0.3 + 0.7 * norm_dirs[i])  # Min radius 30%
            
            wedge = Wedge(
                (plot_x, plot_y), r,
                theta1, theta2,
                facecolor=colors[i % len(colors)],
                edgecolor=edge_color,
                linewidth=1,
                alpha=alpha
            )
            patches.append(wedge)
            ax.add_patch(wedge)
            
            # Add percentage label
            if show_labels and percentages[i] >= 5:  # Only show if >= 5%
                mid_angle = np.radians((theta1 + theta2) / 2)
                label_r = r * 0.65
                lx = plot_x + label_r * np.cos(mid_angle)
                ly = plot_y + label_r * np.sin(mid_angle)
                ax.text(lx, ly, f'{percentages[i]:.0f}%',
                       ha='center', va='center',
                       fontsize=7, fontweight='bold',
                       color='white' if norm_dirs[i] > 0.5 else '#333333')
        
        # Draw center circle
        center = Circle((plot_x, plot_y), zone_size * 0.15,
                        facecolor=center_color, edgecolor=edge_color,
                        linewidth=1.5, zorder=10)
        ax.add_patch(center)
        
        all_patches.extend(patches)
    
    return all_patches


def create_zone_grid(court, rows=2, cols=3, half=True):
    """
    Create a grid of zone centers for sonar charts.
    
    Parameters
    ----------
    court : TennisCourt
        Court object.
    rows : int, default 2
        Number of rows.
    cols : int, default 3
        Number of columns.
    half : bool, default True
        If True, use half court dimensions.
    
    Returns
    -------
    zones : list of dict
        Zone centers with empty direction lists.
    """
    if half:
        x_min, x_max = -4.115, 4.115  # Singles court width
        y_min, y_max = 0, 11.89
    else:
        x_min, x_max = -4.115, 4.115
        y_min, y_max = -11.89, 11.89
    
    # Calculate zone centers
    x_step = (x_max - x_min) / cols
    y_step = (y_max - y_min) / rows
    
    zones = []
    for r in range(rows):
        for c in range(cols):
            x = x_min + (c + 0.5) * x_step
            y = y_min + (r + 0.5) * y_step
            zones.append({'x': x, 'y': y, 'directions': []})
    
    return zones


def sonar_from_shots(ax, shot_x, shot_y, shot_dx, shot_dy,
                     court=None, n_zones_x=3, n_zones_y=2,
                     n_directions=6, zone_size=1.5, half=True,
                     cmap='bsu', **kwargs):
    """
    Create sonar chart from raw shot data.
    
    Parameters
    ----------
    ax : matplotlib axes
        Axes to draw on.
    shot_x, shot_y : array-like
        Shot origin coordinates.
    shot_dx, shot_dy : array-like
        Shot direction vectors (destination - origin).
    court : TennisCourt, optional
        Court object.
    n_zones_x : int, default 3
        Number of zones across court width.
    n_zones_y : int, default 2
        Number of zones along court length.
    n_directions : int, default 6
        Direction segments per zone.
    zone_size : float, default 1.5
        Sonar chart radius.
    half : bool, default True
        Half court mode.
    cmap : str, default 'bsu'
        Color scheme.
    
    Returns
    -------
    patches : list
    """
    shot_x = np.array(shot_x)
    shot_y = np.array(shot_y)
    shot_dx = np.array(shot_dx)
    shot_dy = np.array(shot_dy)
    
    # Calculate shot angles
    angles = np.degrees(np.arctan2(shot_dy, shot_dx))  # -180 to 180
    angles = (90 - angles) % 360  # Convert to 0=up, clockwise
    
    # Define zone boundaries
    if half:
        x_min, x_max = -4.115, 4.115
        y_min, y_max = 0, 11.89
    else:
        x_min, x_max = -4.115, 4.115
        y_min, y_max = -11.89, 11.89
    
    x_edges = np.linspace(x_min, x_max, n_zones_x + 1)
    y_edges = np.linspace(y_min, y_max, n_zones_y + 1)
    
    # Build zone data
    zone_data = []
    angle_step = 360 / n_directions
    
    for i in range(n_zones_y):
        for j in range(n_zones_x):
            # Zone center
            cx = (x_edges[j] + x_edges[j+1]) / 2
            cy = (y_edges[i] + y_edges[i+1]) / 2
            
            # Find shots in this zone
            in_zone = (
                (shot_x >= x_edges[j]) & (shot_x < x_edges[j+1]) &
                (shot_y >= y_edges[i]) & (shot_y < y_edges[i+1])
            )
            zone_angles = angles[in_zone]
            
            # Count shots in each direction bin
            directions = []
            for d in range(n_directions):
                angle_start = (d * angle_step) % 360
                angle_end = ((d + 1) * angle_step) % 360
                
                if angle_start < angle_end:
                    count = np.sum((zone_angles >= angle_start) & (zone_angles < angle_end))
                else:  # Wrap around 360
                    count = np.sum((zone_angles >= angle_start) | (zone_angles < angle_end))
                directions.append(count)
            
            zone_data.append({'x': cx, 'y': cy, 'directions': directions})
    
    return sonar_chart(ax, zone_data, court=court, 
                       n_directions=n_directions, zone_size=zone_size,
                       cmap=cmap, **kwargs)
