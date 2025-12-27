
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
from scipy.stats import gaussian_kde
from .pitch import TennisCourt

def joint_plot(x, y, kind='scatter', title=None, 
               categorical=False, 
               scatter_kws=None, kde_kws=None, hist_kws=None, marginal_kws=None,
               orientation='vertical', half=False, theme='bsu', 
               ax=None, fig=None):
    """
    Create a Joint Plot with Tennis Court and Marginal Distributions.
    Inspired by mplsoccer.Pitch.jointgrid.
    
    Parameters
    ----------
    x, y : array-like
        Coordinates of events.
    kind : str
        'scatter', 'kde', 'hexbin'. Main plot type.
    title : str, optional
    categorical : bool
         Not used yet, placeholder for future categorical marginals.
    scatter_kws : dict, optional
        Keywords for scatter plot.
    kde_kws : dict, optional
        Keywords for main KDE plot (if kind='kde').
    hist_kws : dict, optional
        Keywords for marginal histograms/KDEs.
    marginal_kws : dict, optional
        Keywords for marginal plots (color, etc).
    orientation, half, theme : 
        TennisCourt parameters.
    """
    
    if scatter_kws is None: scatter_kws = {}
    if kde_kws is None: kde_kws = {}
    if hist_kws is None: hist_kws = {}
    if marginal_kws is None: marginal_kws = {}
    
    # Default colors
    if 'color' not in marginal_kws:
        marginal_kws['color'] = '#4c72b0' # Standard blue
        
    x = np.array(x)
    y = np.array(y)

    # Create Figure and Grid
    if fig is None:
        fig = plt.figure(figsize=(10, 10) if orientation=='vertical' else (12, 8))
    
    # GridSpec setup: Central plot + Top + Right
    # Ratios: Marginal usually smaller (e.g. 15%)
    gs = GridSpec(4, 4, figure=fig, 
                  width_ratios=[4, 1, 0.1, 0.1] if orientation=='vertical' else [4, 1, 0.5, 0.5],
                  height_ratios=[1, 4, 0.1, 0.1])
                  
    # Layout:
    # Top Marginal: [0, 0]
    # Main Plot:    [1, 0]
    # Right Marginal: [1, 1]
    
    ax_main = fig.add_subplot(gs[1, 0])
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_main)
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main)
    
    # Draw Court
    court = TennisCourt(orientation=orientation, half=half, theme=theme)
    court.draw(ax=ax_main)
    
    # Plot Main Data
    # Transform data for plotting logic is handled by court methods mostly,
    # BUT for marginals we need the transformed data directly to plot 1D distributions.
    # So let's transform x, y manually to match ax_main's coordinate system.
    
    if orientation == 'vertical':
        plot_x, plot_y = y, x
        xlim = (court.x_min, court.x_max)
        ylim = (court.y_min, court.y_max)
    else:
        plot_x, plot_y = x, y
        xlim = (court.x_min, court.x_max)
        ylim = (court.y_min, court.y_max)

    # Main Plot
    if kind == 'scatter':
        court.scatter(ax_main, x, y, **scatter_kws)
    elif kind == 'kde':
        court.kdeplot(ax_main, x, y, **kde_kws)
    elif kind == 'hexbin':
        court.hexbin(ax_main, x, y, **kde_kws) # Recycle kde_kws or add hexbin_kws?
        
    # Marginals (Top -> X Distribution)
    # Using simple fill_between with gaussian_kde
    try:
        kde_x = gaussian_kde(plot_x)
        x_grid = np.linspace(xlim[0] - 2, xlim[1] + 2, 200)
        ax_top.fill_between(x_grid, kde_x(x_grid), color=marginal_kws['color'], alpha=0.7)
        ax_top.plot(x_grid, kde_x(x_grid), color=marginal_kws['color'])
    except Exception as e:
        # Fallback if singular matrix etc
        ax_top.hist(plot_x, bins=30, density=True, color=marginal_kws['color'], alpha=0.7)

    # Marginals (Right -> Y Distribution)
    try:
        kde_y = gaussian_kde(plot_y)
        y_grid = np.linspace(ylim[0] - 2, ylim[1] + 2, 200)
        # Plot sideways: x = density, y = grid
        ax_right.fill_betweenx(y_grid, kde_y(y_grid), color=marginal_kws['color'], alpha=0.7)
        ax_right.plot(kde_y(y_grid), y_grid, color=marginal_kws['color'])
    except Exception:
        ax_right.hist(plot_y, bins=30, density=True, orientation='horizontal', color=marginal_kws['color'], alpha=0.7)
        
    # Styling Marginals
    ax_top.axis('off')
    ax_right.axis('off')
    
    # Title
    if title:
        fig.suptitle(title, fontsize=16, y=0.95)
        
    return fig, [ax_main, ax_top, ax_right]
