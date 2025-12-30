"""
Joint Plot with Marginal Distributions for Tennis Court
Inspired by mplsoccer's joint plot with marginal axes flush to pitch boundaries
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy import stats
from .pitch import TennisCourt


def joint_plot(x1, y1, x2=None, y2=None, kind='kde', half=False, 
               color1='#92e3da', color2='#9b59b6', 
               label1='Player A', label2='Player B',
               theme='bsu', figsize=None, grid_bins=(6, 3), **kwargs):
    """
    Create a joint plot with marginal distributions for tennis court.
    """
    
    # Smart orientation: Vertical for half court, Horizontal for full court
    orientation = 'vertical' if half else 'horizontal'
    court = TennisCourt(orientation=orientation, half=half, theme=theme)
    
    if half:
        # Vertical Half Court Layout
        if figsize is None:
            figsize = (8, 10)  # Taller for vertical
        
        fig = plt.figure(figsize=figsize, facecolor='white')
        
        # GridSpec: Top Marginal | Empty
        #           Court        | Right Marginal
        gs = gridspec.GridSpec(2, 2, 
                               width_ratios=[1, 0.15],  # Court | Right Marginal (Length dist)
                               height_ratios=[0.15, 1], # Top Marginal (Width dist @ Baseline) | Court
                               wspace=0.02, hspace=0.02)
        
        ax_court = fig.add_subplot(gs[1, 0])
        ax_top = fig.add_subplot(gs[0, 0], sharex=ax_court)
        ax_right = fig.add_subplot(gs[1, 1], sharey=ax_court)
        ax_left = None
        
        # Draw vertical court
        court.draw(ax=ax_court)
        
        # For vertical court: x=width, y=length. No swap needed.
        plot_x1, plot_y1 = np.array(x1), np.array(y1)
        if x2 is not None:
            plot_x2, plot_y2 = np.array(x2), np.array(y2)
            
        # Draw Marginals
        # Top: Width distribution (x-axis)
        _draw_marginal_top(ax_top, plot_x1, color1, court, alpha=0.4, vertical=True)
        if x2 is not None:
             _draw_marginal_top(ax_top, plot_x2, color2, court, alpha=0.4, vertical=True)
             
        # Right: Length distribution (y-axis)
        _draw_marginal_right(ax_right, plot_y1, color1, court, alpha=0.4, vertical=True)
        if x2 is not None:
            _draw_marginal_right(ax_right, plot_y2, color2, court, alpha=0.4, vertical=True)
            
        # Style Marginals
        ax_top.set_xlim(court.x_min, court.x_max)
        ax_top.axis('off')
        
        ax_right.set_ylim(court.y_min, court.y_max)
        ax_right.axis('off')

    else:
        # Horizontal Full Court Layout
        if figsize is None:
            figsize = (14, 8)
            
        fig = plt.figure(figsize=figsize, facecolor='white')
        
        gs = gridspec.GridSpec(2, 3, 
                               width_ratios=[0.08, 1, 0.08],
                               height_ratios=[0.15, 1],
                               wspace=0.02, hspace=0.02)
        
        ax_court = fig.add_subplot(gs[1, 1])
        ax_top = fig.add_subplot(gs[0, 1], sharex=ax_court)
        ax_left = fig.add_subplot(gs[1, 0], sharey=ax_court)
        ax_right = fig.add_subplot(gs[1, 2], sharey=ax_court)
        
        court.draw(ax=ax_court)
        
        # Horizontal: Swap x/y -> plot_x=y, plot_y=x
        plot_x1, plot_y1 = np.array(y1), np.array(x1)
        if x2 is not None:
            plot_x2, plot_y2 = np.array(y2), np.array(x2)
            
        # Draw Marginals
        _draw_marginal_top(ax_top, plot_x1, color1, court, alpha=0.4, vertical=False)
        if x2 is not None:
            _draw_marginal_top(ax_top, plot_x2, color2, court, alpha=0.4, vertical=False)
            
        _draw_marginal_left(ax_left, plot_y2 if x2 is not None else [], color2, court, alpha=0.4, vertical=False)
        _draw_marginal_right(ax_right, plot_y1, color1, court, alpha=0.4, vertical=False)

        ax_top.set_xlim(court.y_min, court.y_max)
        ax_top.axis('off')
        
        ax_left.set_ylim(court.x_min, court.x_max)
        ax_left.axis('off')
        ax_left.invert_xaxis()
        
        ax_right.set_ylim(court.x_min, court.x_max)
        ax_right.axis('off')

    # Main Visualization
    if kind == 'scatter':
        ax_court.scatter(plot_x1, plot_y1, c=color1, s=30, alpha=0.6, 
                        edgecolors='white', linewidths=0.5, label=label1)
        if x2 is not None:
            ax_court.scatter(plot_x2, plot_y2, c=color2, s=30, alpha=0.6,
                            edgecolors='white', linewidths=0.5, label=label2)
    
    elif kind == 'kde':
        if len(plot_x1) > 2:
            try:
                kde1 = stats.gaussian_kde([plot_x1, plot_y1])
                # Grid range based on orientation
                if half:
                    xgrid = np.linspace(court.x_min, court.x_max, 100)
                    ygrid = np.linspace(court.y_min, court.y_max, 100)
                else:
                    xgrid = np.linspace(court.y_min, court.y_max, 100)
                    ygrid = np.linspace(court.x_min, court.x_max, 100)
                    
                X, Y = np.meshgrid(xgrid, ygrid)
                Z1 = kde1([X.ravel(), Y.ravel()]).reshape(X.shape)
                ax_court.contourf(X, Y, Z1, levels=50, cmap=_create_cmap(color1), alpha=0.6)
            except:
                pass
                
        if x2 is not None and len(plot_x2) > 2:
            try:
                kde2 = stats.gaussian_kde([plot_x2, plot_y2])
                Z2 = kde2([X.ravel(), Y.ravel()]).reshape(X.shape)
                ax_court.contourf(X, Y, Z2, levels=50, cmap=_create_cmap(color2), alpha=0.6)
            except:
                pass

    elif kind == 'grid':
        y_bins, x_bins = grid_bins
        if half:
             # Vertical: bins[0]=y(length), bins[1]=x(width) ? standard grid_bins=(y,x)
             # usually bins=(rows, cols) -> (y_bins, x_bins)
             x_edges = np.linspace(court.x_min, court.x_max, x_bins + 1)
             y_edges = np.linspace(court.y_min, court.y_max, y_bins + 1)
             extent = [court.x_min, court.x_max, court.y_min, court.y_max]
        else:
             x_edges = np.linspace(court.y_min, court.y_max, x_bins + 1)
             y_edges = np.linspace(court.x_min, court.x_max, y_bins + 1)
             extent = [court.y_min, court.y_max, court.x_min, court.x_max]

        if len(plot_x1) > 0:
            H1, _, _ = np.histogram2d(plot_x1, plot_y1, bins=[x_edges, y_edges])
            ax_court.imshow(H1.T, extent=extent,
                           origin='lower', cmap=_create_cmap(color1), alpha=0.6, aspect='auto')
        if x2 is not None and len(plot_x2) > 0:
            H2, _, _ = np.histogram2d(plot_x2, plot_y2, bins=[x_edges, y_edges])
            ax_court.imshow(H2.T, extent=extent,
                           origin='lower', cmap=_create_cmap(color2), alpha=0.6, aspect='auto')

    # Player Labels
    if not half:
        ax_court.text(court.y_max - 1, court.x_min - 0.8, label1,
                     fontsize=14, color=color1, weight='bold', ha='right')
        if x2 is not None:
             ax_court.text(court.y_min + 1, court.x_min - 0.8, label2,
                          fontsize=14, color=color2, weight='bold', ha='left')
    else:
        # Half court labels: Bottom Center
        # Position slightly below the net (y=0)
        ax_court.text(0, -1, label1,
                     fontsize=14, color=color1, weight='bold', ha='center', va='top')
        
        # Extend Net Line visually
        # Standard net extends 0.914m beyond sidelines
        # Sidelines are at x=-5.485 and x=5.485
        net_width_half = 5.485 + 0.914 + 1
        ax_court.plot([-net_width_half, net_width_half], [0, 0], 
                     color='black', linewidth=2, zorder=10)

    # Force auto aspect ratio
    ax_court.set_aspect('auto')
    
    return fig, ax_court

def _create_cmap(color):
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("custom", ['#ffffff', color], N=100)

def _draw_marginal_top(ax, x_data, color, court, alpha=0.4, vertical=False):
    if len(x_data) < 2: return
    try:
        kde = stats.gaussian_kde(x_data)
        if vertical:
            x_grid = np.linspace(court.x_min, court.x_max, 200)
        else:
            x_grid = np.linspace(court.y_min, court.y_max, 200)
        density = kde(x_grid)
        ax.fill_between(x_grid, 0, density, color=color, alpha=alpha, linewidth=0)
        ax.plot(x_grid, density, color=color, linewidth=1, alpha=0.8)
    except: pass

def _draw_marginal_left(ax, y_data, color, court, alpha=0.4, vertical=False):
    if len(y_data) < 2: return
    try:
        kde = stats.gaussian_kde(y_data)
        if vertical: # usually only right marginal for vertical half court
             y_grid = np.linspace(court.y_min, court.y_max, 200)
        else:
             y_grid = np.linspace(court.x_min, court.x_max, 200)
        density = kde(y_grid)
        ax.fill_betweenx(y_grid, 0, density, color=color, alpha=alpha, linewidth=0)
        ax.plot(density, y_grid, color=color, linewidth=1, alpha=0.8)
    except: pass

def _draw_marginal_right(ax, y_data, color, court, alpha=0.4, vertical=False):
    if len(y_data) < 2: return
    try:
        kde = stats.gaussian_kde(y_data)
        if vertical:
             y_grid = np.linspace(court.y_min, court.y_max, 200)
        else:
             y_grid = np.linspace(court.x_min, court.x_max, 200)
        density = kde(y_grid)
        ax.fill_betweenx(y_grid, 0, density, color=color, alpha=alpha, linewidth=0)
        ax.plot(density, y_grid, color=color, linewidth=1, alpha=0.8)
    except: pass
