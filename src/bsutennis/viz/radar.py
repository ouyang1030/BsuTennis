"""
Radar Chart for Tennis Player Comparison
Inspired by mplsoccer's radar chart functionality
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes


class Radar:
    """
    A class to create radar charts for comparing tennis player statistics.
    
    Parameters
    ----------
    params : list of str
        List of parameter names to display on the radar chart.
    min_range : list of float, optional
        Minimum values for each parameter. If None, uses 0 for all.
    max_range : list of float, optional
        Maximum values for each parameter. If None, uses 100 for all.
    
    Examples
    --------
    >>> params = ['Serve Speed', 'First Serve %', 'Aces', 'Winners', 'Break Points Won']
    >>> radar = Radar(params, min_range=[0, 0, 0, 0, 0], max_range=[220, 100, 20, 50, 100])
    >>> fig, ax = radar.setup_axis()
    >>> radar.draw_circles(ax)
    >>> radar.draw(ax, [200, 65, 12, 35, 45], label='Player A', color='#e74c3c')
    >>> radar.draw(ax, [190, 70, 8, 40, 50], label='Player B', color='#3498db')
    >>> plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    >>> plt.show()
    """
    
    def __init__(self, params, min_range=None, max_range=None):
        self.params = params
        self.n_params = len(params)
        
        if min_range is None:
            self.min_range = [0] * self.n_params
        else:
            self.min_range = min_range
            
        if max_range is None:
            self.max_range = [100] * self.n_params
        else:
            self.max_range = max_range
    
    def normalize_values(self, values):
        """Normalize values to 0-1 range based on min/max ranges."""
        normalized = []
        for val, min_val, max_val in zip(values, self.min_range, self.max_range):
            norm = (val - min_val) / (max_val - min_val)
            normalized.append(max(0, min(1, norm)))  # Clamp to [0, 1]
        return normalized
    
    def setup_axis(self, figsize=(8, 8), facecolor='white'):
        """Create and return figure and polar axis."""
        fig = plt.figure(figsize=figsize, facecolor=facecolor)
        ax = fig.add_subplot(111, projection='polar')
        ax.set_facecolor(facecolor)
        
        # Set theta direction and offset
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Remove default polar grid
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.spines['polar'].set_visible(False)
        
        # Set parameter labels
        angles = np.linspace(0, 2 * np.pi, self.n_params, endpoint=False).tolist()
        ax.set_xticks(angles)
        ax.set_xticklabels(self.params, size=10)
        
        return fig, ax
    
    def draw_circles(self, ax, num_rings=5, color='#d3d3d3', linewidth=1):
        """Draw concentric circles as background grid."""
        for i in range(1, num_rings + 1):
            circle_val = i / num_rings
            angles = np.linspace(0, 2 * np.pi, 100)
            ax.plot(angles, [circle_val] * len(angles), 
                   color=color, linewidth=linewidth, linestyle='-', alpha=0.5)
    
    def draw(self, ax, values, label=None, color='#3498db', alpha=0.25, linewidth=2):
        """
        Draw a player's statistics on the radar chart.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The polar axis to draw on.
        values : list of float
            The values for each parameter.
        label : str, optional
            Label for the legend.
        color : str, optional
            Color for the plot.
        alpha : float, optional
            Transparency for the filled area.
        linewidth : float, optional
            Width of the outline.
        """
        # Normalize values
        norm_values = self.normalize_values(values)
        
        # Close the plot by appending the first value
        norm_values += norm_values[:1]
        
        # Calculate angles
        angles = np.linspace(0, 2 * np.pi, self.n_params, endpoint=False).tolist()
        angles += angles[:1]
        
        # Plot
        ax.plot(angles, norm_values, color=color, linewidth=linewidth, label=label)
        ax.fill(angles, norm_values, color=color, alpha=alpha)
