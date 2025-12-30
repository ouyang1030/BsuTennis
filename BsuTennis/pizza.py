"""
Pizza Chart Visualization for Tennis Analytics.

Creates radial bar charts (pizza charts) for displaying player statistics
in a visually appealing format, popular in sports analytics.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Wedge
import numpy as np


def pizza_chart(params, values, 
                title='Player Performance',
                compare_values=None,
                compare_label=None,
                colors=None,
                slice_colors=None,
                text_colors=None,
                figsize=(10, 10),
                inner_circle_size=0.4,
                fontfamily='DejaVu Sans',
                title_fontsize=24,
                param_fontsize=11,
                value_fontsize=10,
                theme='dark',
                **kwargs):
    """
    Create a pizza chart for player statistics.
    
    Parameters
    ----------
    params : list of str
        Parameter names (e.g., ['Aces', 'Winners', '1st Serve %', ...]).
    values : list of float
        Values for each parameter (0-100 scale recommended).
    title : str
        Chart title (player name or description).
    compare_values : list of float, optional
        Optional second set of values to compare.
    compare_label : str, optional
        Label for comparison values.
    colors : list of str, optional
        Custom colors for each slice. If None, uses gradient.
    slice_colors : dict, optional
        Override colors for specific slices by index.
    text_colors : dict, optional
        Override text colors for specific slices.
    figsize : tuple, default (10, 10)
        Figure size.
    inner_circle_size : float, default 0.4
        Size of inner circle (0-1 scale).
    fontfamily : str, default 'DejaVu Sans'
        Font family for text.
    title_fontsize : int, default 24
        Title font size.
    param_fontsize : int, default 11
        Parameter label font size.
    value_fontsize : int, default 10
        Value label font size.
    theme : str, default 'dark'
        Color theme: 'dark', 'light', or 'bsu'.
    
    Returns
    -------
    fig, ax : matplotlib figure and axes
    """
    
    n = len(params)
    if len(values) != n:
        raise ValueError("Length of params and values must match")
    
    # Theme settings
    themes = {
        'dark': {
            'bg': '#1a1a2e',
            'text': '#ffffff',
            'inner': '#16213e',
            'grid': '#0f3460',
            'gradient': ['#e94560', '#ff6b6b', '#ffa502', '#2ed573', '#1e90ff', '#a55eea'],
        },
        'light': {
            'bg': '#ffffff',
            'text': '#2d2d2d',
            'inner': '#f0f0f0',
            'grid': '#e0e0e0',
            'gradient': ['#e74c3c', '#e67e22', '#f1c40f', '#27ae60', '#3498db', '#9b59b6'],
        },
        'bsu': {
            'bg': '#0d1b2a',
            'text': '#ffffff',
            'inner': '#1b263b',
            'grid': '#415a77',
            'gradient': ['#92e3da', '#5bc0be', '#3a86ff', '#8338ec', '#ff006e', '#fb5607'],
        }
    }
    
    t = themes.get(theme, themes['dark'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': 'polar'})
    fig.patch.set_facecolor(t['bg'])
    ax.set_facecolor(t['bg'])
    
    # Calculate angles
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    # Close the plot
    angles += angles[:1]
    values_plot = values + values[:1]
    
    # Generate colors if not provided
    if colors is None:
        # Create smooth gradient
        base_colors = t['gradient']
        colors = []
        for i in range(n):
            idx = int(i * len(base_colors) / n) % len(base_colors)
            colors.append(base_colors[idx])
    
    # Apply slice color overrides
    if slice_colors:
        for idx, color in slice_colors.items():
            if idx < len(colors):
                colors[idx] = color
    
    # Draw slices (pie wedges)
    width = (2 * np.pi) / n
    for i in range(n):
        # Calculate wedge parameters
        theta1 = np.degrees(angles[i] - width/2)
        theta2 = np.degrees(angles[i] + width/2)
        
        # Normalize value to radius (0-1 range, where 1 is edge)
        r = max(0.1, min(values[i] / 100, 1.0))  # Clamp between 0.1 and 1.0
        
        # Draw the slice
        ax.bar(angles[i], r, width=width * 0.92, bottom=inner_circle_size,
               color=colors[i % len(colors)], alpha=0.85, edgecolor='white', linewidth=0.5)
        
        # Draw comparison values if provided
        if compare_values is not None:
            r_compare = max(0.05, min(compare_values[i] / 100, 1.0))
            ax.bar(angles[i], r_compare, width=width * 0.3, bottom=inner_circle_size,
                   color='white', alpha=0.4, edgecolor='none')
    
    # Draw parameter labels
    for i, param in enumerate(params):
        angle = angles[i]
        
        # Calculate label position (outside the chart)
        label_r = 1.15
        
        # Rotate text based on position
        rotation = np.degrees(angle) - 90
        if angle > np.pi / 2 and angle < 3 * np.pi / 2:
            rotation += 180
            ha = 'right'
        else:
            ha = 'left'
        
        # Get text color
        text_color = t['text']
        if text_colors and i in text_colors:
            text_color = text_colors[i]
        
        # Draw parameter name
        ax.text(angle, label_r, param, 
                ha='center', va='center',
                fontsize=param_fontsize, 
                fontfamily=fontfamily,
                fontweight='bold',
                color=text_color)
        
        # Draw value
        value_r = inner_circle_size + (values[i] / 100) / 2 + 0.08
        if values[i] > 50:
            value_color = 'white'
        else:
            value_color = colors[i % len(colors)]
        
        ax.text(angle, value_r, f'{values[i]:.0f}',
                ha='center', va='center',
                fontsize=value_fontsize,
                fontfamily=fontfamily,
                fontweight='bold',
                color=value_color if values[i] > 30 else t['text'],
                alpha=0.9)
    
    # Style the polar plot
    ax.set_ylim(0, 1.2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['polar'].set_visible(False)
    
    # Draw inner circle
    inner = plt.Circle((0, 0), inner_circle_size, transform=ax.transData._b,
                        facecolor=t['inner'], edgecolor='white', linewidth=2, zorder=10)
    ax.add_patch(inner)
    
    # Add title in center
    ax.text(0, 0, title, ha='center', va='center', 
            fontsize=title_fontsize, fontfamily=fontfamily,
            fontweight='bold', color=t['text'],
            transform=ax.transData._b, zorder=11)
    
    # Add comparison legend if needed
    if compare_values is not None and compare_label:
        legend_patch = mpatches.Patch(color='white', alpha=0.4, label=compare_label)
        ax.legend(handles=[legend_patch], loc='upper right', 
                 facecolor=t['bg'], edgecolor='none',
                 fontsize=10, labelcolor=t['text'])
    
    plt.tight_layout()
    return fig, ax


def pizza(player_name, stats_dict, theme='bsu', **kwargs):
    """
    Create a tennis-specific pizza chart.
    
    Parameters
    ----------
    player_name : str
        Name of the player.
    stats_dict : dict
        Dictionary of stat name -> value (0-100).
        Example: {'Aces': 85, 'Winners': 72, '1st Serve %': 68, ...}
    theme : str, default 'bsu'
        Color theme: 'dark', 'bsu'.
    **kwargs : additional arguments passed to pizza_chart
    
    Returns
    -------
    fig, ax : matplotlib figure and axes
    """
    params = list(stats_dict.keys())
    values = list(stats_dict.values())
    
    return pizza_chart(params, values, title=player_name, theme=theme, **kwargs)
