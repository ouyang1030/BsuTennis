
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

class Radar:
    """
    Radar chart class mimicking mplsoccer API.
    """
    def __init__(self, params, low, high, lower_is_better=None, round_int=None,
                 num_rings=4, ring_width=1, center_circle_radius=1):
        self.params = params
        self.low = np.array(low)
        self.high = np.array(high)
        self.num_rings = num_rings
        self.ring_width = ring_width
        self.center_circle_radius = center_circle_radius
        
        if lower_is_better is None:
            self.lower_is_better = []
        else:
            self.lower_is_better = lower_is_better
            
        # Determine angles
        self.num_params = len(params)
        self.angles = np.linspace(0, 2*np.pi, self.num_params, endpoint=False)
        self.angles = np.concatenate((self.angles, [self.angles[0]]))
        
        # Ranges
        self.ranges = self.high - self.low
        
    def setup_axis(self, ax=None, facecolor='white', **kwargs):
        """Setup the polar axis."""
        if ax is None:
            fig = plt.figure(facecolor=facecolor)
            ax = fig.add_subplot(111, polar=True, **kwargs)
        else:
            fig = ax.figure
            
        ax.set_facecolor(facecolor)
        
        # Hide standard grid and spines
        ax.grid(False)
        ax.spines['polar'].set_visible(False)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        
        return fig, ax
        
    def _normalize(self, values):
        """Normalize values to match the radar range."""
        norm_values = []
        for i, (val, lo, hi, label) in enumerate(zip(values, self.low, self.high, self.params)):
            if label in self.lower_is_better:
                # Invert logic: Lower is better means closer to center? 
                # Usually radar charts: center is "bad" (0) or "low", outer is "good".
                # If lower is better, then low value -> outer edge (high score), high value -> center (low score).
                # Normalized = (High - Val) / (High - Low)
                n = (hi - val) / (hi - lo)
            else:
                # Standard: (Val - Low) / (High - Low)
                n = (val - lo) / (hi - lo)
            
            # Clip 0-1
            n = np.clip(n, 0, 1)
            norm_values.append(n)
            
        return np.array(norm_values)
        
    def _scale_to_rings(self, norm_values):
        """Scale normalized 0-1 values to the ring coordinates."""
        # 0 -> center_circle_radius
        # 1 -> center_circle_radius + num_rings * ring_width
        return self.center_circle_radius + norm_values * (self.num_rings * self.ring_width)

    def draw_circles(self, ax, facecolor='none', edgecolor='#D4D4D4', **kwargs):
        """Draw the background rings."""
        rings = []
        for i in range(self.num_rings + 1):
            radius = self.center_circle_radius + i * self.ring_width
            # Draw circle
            # Using plot for circles in polar coords
            x = np.linspace(0, 2*np.pi, 200)
            y = np.full_like(x, radius)
            l = ax.plot(x, y, color=edgecolor, linewidth=1, zorder=0)
            rings.append(l)
            
            # Fill logic if needed (not strictly circles but alternating bands usually)
            
        # Draw center circle
        # ax.fill_between(x, 0, self.center_circle_radius, color=facecolor)
        # We can simulate fill by filling the largest circle with background
        
        return rings

    def draw_radar_solid(self, values, ax, kwargs=None):
        """Draw the filled radar polygon."""
        if kwargs is None:
            kwargs = {}
            
        norm_values = self._normalize(values)
        scaled_values = self._scale_to_rings(norm_values)
        
        # Close loop
        scaled_values = np.concatenate((scaled_values, [scaled_values[0]]))
        
        # Plot
        line, = ax.plot(self.angles, scaled_values, **{k:v for k,v in kwargs.items() if k!='alpha' and k!='facecolor'})
        
        # Fill
        poly = ax.fill(self.angles, scaled_values, zorder=kwargs.get('zorder', 2), **{k:v for k,v in kwargs.items() if k!='lw' and k!='linewidth' and k!='linestyle'})
        
        return line, poly

    def draw_param_labels(self, ax, fontsize=10, pad=15, **kwargs):
        """Draw labels for each parameter."""
        labels = []
        outer_radius = self.center_circle_radius + self.num_rings * self.ring_width
        
        # Using self.params (not closed)
        for angle, label in zip(self.angles[:-1], self.params):
            # Calculate position
            # Add padding
            # Convert polar to cartesian to add offset? No, just use R + pad
            # But "pad" in polar is just more radius? Or pixel offset?
            # Easier to use text alignment.
            
            # Rotation
            rot = angle * 180 / np.pi
            # if 90 < rot < 270:
            #     rot += 180
            
            # Alignment
            ha = 'center'
            # if 0 <= angle < np.pi/2 or 3*np.pi/2 < angle <= 2*np.pi:
            #     ha = 'left'
            # else:
            #     ha = 'right'
            
            # Distance: The text needs to be slightly outside the last ring.
            # We can use ax.text(angle, radius, ...)
            
            # A simple heuristic for distance
            dist = outer_radius + (self.ring_width * 0.5) 
            
            t = ax.text(angle, dist, label, ha='center', va='center', fontsize=fontsize, **kwargs)
            labels.append(t)
            
        return labels

    def draw_range_labels(self, ax, fontsize=10, **kwargs):
        """Draw scale labels."""
        # Typically on the vertical axis (angle 0 or pi/2)
        return []

