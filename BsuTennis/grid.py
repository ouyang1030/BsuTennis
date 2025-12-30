"""
Grid Layout Utilities for Multi-Court Visualizations
"""

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from .pitch import TennisCourt


def create_court_grid(nrows=1, ncols=3, orientation='vertical', half=True, 
                      theme='bsu', figsize=None, **court_kwargs):
    """
    Create a grid of tennis courts for multi-player or multi-scenario comparison.
    
    Parameters
    ----------
    nrows : int, default 1
        Number of rows in the grid.
    ncols : int, default 3
        Number of columns in the grid.
    orientation : str, default 'vertical'
        Court orientation ('vertical' or 'horizontal').
    half : bool, default True
        Whether to draw half courts (recommended for grids).
    theme : str, default 'bsu'
        Color theme for all courts.
    figsize : tuple, optional
        Figure size (width, height). If None, auto-calculated based on grid size.
    **court_kwargs : dict
        Additional arguments passed to TennisCourt initialization.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure containing the grid.
    axes : numpy.ndarray
        Array of axes (shape: nrows × ncols).
    courts : list
        List of TennisCourt instances (flattened).
        
    Examples
    --------
    >>> fig, axes, courts = create_court_grid(nrows=2, ncols=3)
    >>> # Draw on each court
    >>> for i, (ax, court) in enumerate(zip(axes.flat, courts)):
    ...     court.draw(ax=ax)
    ...     ax.set_title(f"Player {i+1}")
    >>> plt.tight_layout()
    >>> plt.show()
    """
    # Auto-calculate figsize if not provided
    if figsize is None:
        if orientation == 'vertical':
            # Vertical courts are taller
            cell_width = 3
            cell_height = 4 if half else 6
        else:
            # Horizontal courts are wider
            cell_width = 4 if half else 6
            cell_height = 3
        figsize = (ncols * cell_width, nrows * cell_height)
    
    # Create figure and gridspec
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(nrows, ncols, figure=fig, hspace=0.3, wspace=0.3)
    
    # Create axes and courts
    axes = []
    courts = []
    
    for i in range(nrows):
        row_axes = []
        for j in range(ncols):
            ax = fig.add_subplot(gs[i, j])
            row_axes.append(ax)
            
            # Create court instance
            court = TennisCourt(
                orientation=orientation,
                half=half,
                theme=theme,
                **court_kwargs
            )
            courts.append(court)
        axes.append(row_axes)
    
    # Convert to numpy array for easier indexing
    import numpy as np
    axes = np.array(axes)
    
    return fig, axes, courts
