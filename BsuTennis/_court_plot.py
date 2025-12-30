
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import gaussian_kde

from .dimension import (WIDTH_SINGLES, WIDTH_DOUBLES, HALF_LENGTH, 
                        SERVICE_LINE_DISTANCE, ALLEY_WIDTH)

class CourtPlotMixin:
    """
    Mixin class handling all plotting methods for TennisCourt.
    Inherits geometry from BaseCourt (via MRO in TennisCourt).
    """

    def draw(self, ax=None, color='white', **kwargs):
        """
        Draw the tennis court lines.
        """
        if ax is None:
            ax = plt.gca()
            
        # Set aspect
        ax.set_aspect('equal')
        
        # Colors (provided by init or theme)
        lc = self.line_color
        pc = self.pitch_color
        lw = self.linewidth
        
        w = self.width / 2
        l = HALF_LENGTH
        
        # Draw Background (Rectangle instead of set_facecolor because axis('off') hides it)
        # Draw Background (Rectangle covering extent + padding for 'outer border' effect)
        if pc:
            padding = 2
            # Use extent
            if self.orientation == 'horizontal':
                 bg_w = (self.extent[1] + padding) - (self.extent[0] - padding)
                 bg_h = (self.extent[3] + padding) - (self.extent[2] - padding)
                 x_start = self.extent[0] - padding
                 y_start = self.extent[2] - padding
            else:
                 bg_w = (self.extent[1] + padding) - (self.extent[0] - padding)
                 bg_h = (self.extent[3] + padding) - (self.extent[2] - padding)
                 x_start = self.extent[0] - padding
                 y_start = self.extent[2] - padding
                 
            rect = Rectangle((x_start, y_start), bg_w, bg_h, facecolor=pc, zorder=0)
            ax.add_patch(rect)
            
            # Additional Outer Border/Edge if requested (User asked for circle/perimeter for theme)
            # This large rectangle acts as that 'colored' area.
            
        # LINES GENERATION
        # ... (lines generation logic unchanged here, but we need to ensure flow)
        
        lines = []
        
        # Helper: Add line segment ((x1, y1), (x2, y2))
        def add_line(p1, p2):
            lines.append((p1, p2))
            
        sw = WIDTH_SINGLES / 2
        sl = SERVICE_LINE_DISTANCE
        
        # Baseline (Bottom)
        if not self.half:
            add_line((-w, -l), (w, -l))
            # Baseline (Top)
            add_line((-w, l), (w, l))
            # Sides
            add_line((-w, -l), (-w, l))
            add_line((w, -l), (w, l))
            # Singles Sidelines (Only draw if Doubles court, otherwise they overlap Sides)
            if self.court_type == 'doubles':
                add_line((-sw, -l), (-sw, l))
                add_line((sw, -l), (sw, l))
            
            # Service Lines
            add_line((-sw, -sl), (sw, -sl))
            add_line((-sw, sl), (sw, sl))
            # Center Service Line
            add_line((0, -sl), (0, sl))
            # Center Marks
            add_line((0, -l), (0, -l + 0.1)) # Small mark
            add_line((0, l), (0, l - 0.1))
            
        else:
            # Half Court
            # BaseLine
            add_line((-w, l), (w, l))
            # Sides
            add_line((-w, 0), (-w, l))
            add_line((w, 0), (w, l))
            # Singles Sides
            if self.court_type == 'doubles':
                add_line((-sw, 0), (-sw, l))
                add_line((sw, 0), (sw, l))
            # Service Line
            add_line((-sw, sl), (sw, sl))
            # Center Service Line
            add_line((0, 0), (0, sl))
            # Center Mark
            add_line((0, l), (0, l - 0.15))
            
            
        # Draw Lines
        for p1, p2 in lines:
            x_pts = [p1[0], p2[0]]
            y_pts = [p1[1], p2[1]]
            
            if self.orientation == 'horizontal':
                ax.plot(y_pts, x_pts, color=lc, linewidth=lw, **kwargs)
            else:
                ax.plot(x_pts, y_pts, color=lc, linewidth=lw, **kwargs)

        # Net Logic
        # "Reality": Net posts are 0.914m outside the DOUBLES sidelines for a standard court.
        # Even for singles matches on a standard court, the net is the doubles net supported by singles sticks.
        # So we draw the full realistic net width always.
        
        net_w = (WIDTH_DOUBLES / 2) + 0.914

        if self.orientation == 'horizontal':
            ax.plot([0, 0], [-net_w, net_w], color=lc, linestyle='-', linewidth=lw)
        else:
            ax.plot([-net_w, net_w], [0, 0], color=lc, linestyle='-', linewidth=lw)
            
        # Limits
        if self.orientation == 'horizontal':
             padding = 2
             ax.set_xlim(self.extent[0]-padding, self.extent[1]+padding)
             ax.set_ylim(self.extent[2]-padding, self.extent[3]+padding)
        else:
             padding = 2
             ax.set_xlim(self.extent[0]-padding, self.extent[1]+padding)
             ax.set_ylim(self.extent[2]-padding, self.extent[3]+padding)

        # Remove Axes ticks usually?
        if not self.axis:
            ax.axis('off')
            
    def draw_guides(self, ax, service_vertical_lines=0, backcourt_line=False, color='grey', linestyle='--', linewidth=0.8, alpha=0.5):
        """
        Draw guide lines on top of the court.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes to draw on.
        service_vertical_lines : int, default 0
            Number of lines to split the service zone vertically.
            0: No lines.
            1: Bisect (2 zones, e.g., Left/Right).
            2: Trisect (3 zones, e.g., Wide, Body, T).
        backcourt_line : bool, default False
            If True, draws a horizontal line bisecting the backcourt (No Man's Land).
        """
        sl = SERVICE_LINE_DISTANCE
        ws = WIDTH_SINGLES / 2
        
        # 1. Service Zone Splitters (Vertical/Longitudinal)
        x_lines = []
        if service_vertical_lines == 1:
            # Bisect: Line at 0? No, 0 is Center Line which already exists.
            # Usually "Parallel to long edge" means dividing the BOX itself.
            # The Service Box is 0 to WS.
            # Bisecting it means a line at WS/2.
            x_lines = [ws / 2, -ws / 2]
        elif service_vertical_lines == 2:
            # Trisect: Lines at 1/3 and 2/3
            split_1 = ws / 3
            split_2 = ws * 2 / 3
            x_lines = [split_1, split_2, -split_1, -split_2]
            
        for x_line in x_lines:
            if self.orientation == 'horizontal':
                if self.half:
                     ax.plot([0, sl], [x_line, x_line], color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha)
                else:
                     ax.plot([-sl, sl], [x_line, x_line], color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha)
            else:
                if self.half:
                     ax.plot([x_line, x_line], [0, sl], color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha)
                else:
                     ax.plot([x_line, x_line], [-sl, sl], color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha)

        # 2. Bisect Backcourt (No Man's Land) - Horizontal/Lateral
        if backcourt_line:
            y_back_mid = (SERVICE_LINE_DISTANCE + HALF_LENGTH) / 2
            
            ys = [y_back_mid]
            if not self.half:
                 ys.append(-y_back_mid)
                 
            for y_line in ys:
                if self.orientation == 'horizontal':
                    ax.plot([y_line, y_line], [-ws, ws], color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha)
                else:
                    ax.plot([-ws, ws], [y_line, y_line], color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha)

    # Alias/Deprecation Wrappers
    def draw_bsu_guides(self, ax, **kwargs):
        """Alias for draw_guides with BSU presets (2 lines, True backcourt)."""
        self.draw_guides(ax, service_vertical_lines=2, backcourt_line=True, **kwargs)
        
    def draw_service_zones(self, ax, **kwargs):
        """Deprecated: Use draw_guides instead."""
        self.draw_guides(ax, **kwargs)

    def scatter(self, ax, x, y, style=None, **kwargs):
        from .theme import SCATTER_STYLES
        
        plot_kwargs = {}
        if style:
             if isinstance(style, str) and style in SCATTER_STYLES:
                 plot_kwargs.update(SCATTER_STYLES[style])
        
        plot_kwargs.update(kwargs)
        
        if self.orientation == 'horizontal':
             plot_x, plot_y = y, x 
             # Wait, Input X,Y logic. 
             # If input is Standard Vertical (X=Width), then Horizontal X=Length=Y_input.
             # So we plot (y, x).
             # BUT usually users pass (x,y) in the coord system of the visual?
             # Or (x,y) in data system?
             # BaseCourt assumes data logic?
             # Let's assume input X, Y are ALWAYS Standard Vertical (Data).
             ax.scatter(y, x, **plot_kwargs)
        else:
             ax.scatter(x, y, **plot_kwargs)

    def annotate(self, ax, x, y, text, fontsize=10, color='white', 
                 ha='center', va='center', bbox=None, **kwargs):
        """
        Add text annotation on the court.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes to draw on.
        x, y : float
            Coordinates (in standard vertical court coords).
        text : str
            Text to display.
        fontsize : int, default 10
            Font size.
        color : str, default 'white'
            Text color.
        ha : str, default 'center'
            Horizontal alignment.
        va : str, default 'center'
            Vertical alignment.
        bbox : dict, optional
            Bounding box properties (e.g., {'facecolor': 'black', 'alpha': 0.5}).
        **kwargs : dict
            Additional arguments passed to ax.text().
        
        Returns
        -------
        text : matplotlib.text.Text
        """
        if self.orientation == 'horizontal':
            plot_x, plot_y = y, x
        else:
            plot_x, plot_y = x, y
        
        return ax.text(plot_x, plot_y, text, fontsize=fontsize, color=color,
                       ha=ha, va=va, bbox=bbox, **kwargs)

    def arrows(self, ax, x_start, y_start, x_end, y_end, 
               color='black', linewidth=2, linestyle='solid', 
               arrow_style='fancy', alpha=1.0, **kwargs):
        """
        Draw arrows for shot trajectories.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes to draw on.
        x_start, y_start : array-like
            Starting coordinates.
        x_end, y_end : array-like
            Ending coordinates.
        color : str, default 'black'
            Arrow color.
        linewidth : float, default 2
            Line thickness.
        linestyle : str, default 'solid'
            Line style: 'solid', 'dashed', 'dotted', 'dashdot'.
        arrow_style : str, default 'fancy'
            Arrow head style: 'fancy', 'simple', 'wedge', 'curve'.
        alpha : float, default 1.0
            Transparency (0-1).
        """
        from matplotlib.patches import FancyArrowPatch
        
        if self.orientation == 'horizontal':
            sx, sy = np.array(y_start), np.array(x_start)
            ex, ey = np.array(y_end), np.array(x_end)
        else:
            sx, sy = np.array(x_start), np.array(y_start)
            ex, ey = np.array(x_end), np.array(y_end)
        
        # Arrow style mapping
        arrow_styles = {
            'fancy': '-|>',
            'simple': '->',
            'wedge': '-[',
            'curve': 'fancy',
        }
        style = arrow_styles.get(arrow_style, '-|>')
        
        # Linestyle mapping
        ls_map = {
            'solid': '-',
            'dashed': '--',
            'dotted': ':',
            'dashdot': '-.',
        }
        ls = ls_map.get(linestyle, linestyle)
        
        # Draw each arrow
        for i in range(len(sx)):
            arrow = FancyArrowPatch(
                posA=(sx[i], sy[i]),
                posB=(ex[i], ey[i]),
                arrowstyle=style,
                color=color,
                linewidth=linewidth,
                linestyle=ls,
                alpha=alpha,
                mutation_scale=15,
                shrinkA=0,
                shrinkB=0,
                **kwargs
            )
            ax.add_patch(arrow)

    def kdeplot(self, ax, x, y, cmap='bsu_green', levels=100, clip=None, **kwargs):
        # Custom cmaps
        cmaps = {
            'bsu_green': LinearSegmentedColormap.from_list("bsu_green", ['#ffffff', '#92e3da'], N=100),
            'bsu_red': LinearSegmentedColormap.from_list("bsu_red", ['#ffffff', '#ff3b3b'], N=100),
            'bsu_blue': LinearSegmentedColormap.from_list("bsu_blue", ['#ffffff', '#2437ff'], N=100)
        }
        if cmap in cmaps: cmap = cmaps[cmap]
        
        x = np.array(x); y = np.array(y)
        
        # Grid bounds
        # BaseCourt extent is useful here
        # But we need grid in PLOT coordinates
        if self.orientation == 'horizontal':
             px, py = y, x
             xmin, xmax = self.extent[0], self.extent[1]
             ymin, ymax = self.extent[2], self.extent[3]
        else:
             px, py = x, y
             xmin, xmax = self.extent[0], self.extent[1]
             ymin, ymax = self.extent[2], self.extent[3]
             
        buff = 1
        xx, yy = np.mgrid[xmin-buff:xmax+buff:200j, ymin-buff:ymax+buff:200j]
        positions = np.vstack([xx.ravel(), yy.ravel()])
        values = np.vstack([px, py])
        
        kernel = gaussian_kde(values)
        f = np.reshape(kernel(positions).T, xx.shape)
        
        if clip:
             # Assume clip is in plot coords for now
             cx, cy = clip
             mask = (xx < cx[0]) | (xx > cx[1]) | (yy < cy[0]) | (yy > cy[1])
             f[mask] = 0
             
        return ax.contourf(xx, yy, f, levels=levels, cmap=cmap, **kwargs)

    def _get_extent(self, half):
        # Determine effective half flag
        is_half = half if half is not None else self.half
        
        if self.orientation == 'horizontal':
            if is_half:
                # Horizontal Half: x=0..11.89 (Length), y=-5.485..5.485 (Width)
                return [0, 11.89, -5.485, 5.485]
            else:
                return [self.y_min, self.y_max, self.x_min, self.x_max]
        else:
            if is_half:
                # Vertical Half: x=-5.485..5.485 (Width), y=0..11.89 (Length)
                return [-5.485, 5.485, 0, 11.89]
            else:
                return [self.x_min, self.x_max, self.y_min, self.y_max]

    def heatmap(self, ax, x, y, bins=10, statistic='count', cmap='coolwarm', annot=False, fmt='.0f', half=None, gridsize=None, **kwargs):
        x = np.array(x); y = np.array(y)
        
        # Gridsize alias for bins (consistency with hexbin)
        if gridsize is not None:
            bins = gridsize

        if self.orientation == 'horizontal':
            px, py = y, x
        else:
            px, py = x, y
            
        extent = self._get_extent(half)
        # histogram2d expects range=[[xmin, xmax], [ymin, ymax]]
        bounds = [[extent[0], extent[1]], [extent[2], extent[3]]]

        H, xedges, yedges = np.histogram2d(px, py, bins=bins, range=bounds)
        H = H.T
        
        if statistic == 'frequency':
             H = H / np.sum(H) * 100
             if fmt=='.0f': fmt='.1f'
             
        if 'edgecolor' not in kwargs: kwargs['edgecolor'] = 'white'
        if 'linewidth' not in kwargs: kwargs['linewidth'] = 0.5
        
        mesh = ax.pcolormesh(xedges, yedges, H, cmap=cmap, **kwargs)
        
        if annot:
            xc = (xedges[:-1] + xedges[1:])/2
            yc = (yedges[:-1] + yedges[1:])/2
            for i in range(len(xc)):
                for j in range(len(yc)):
                     if H[j, i] > 0:
                         ax.text(xc[i], yc[j], format(H[j,i], fmt), ha='center', va='center', fontsize=8)
        return mesh

    def hexbin(self, ax, x, y, gridsize=20, cmap='Blues', edgecolors='white', mincnt=1, half=None, **kwargs):
        # Resolve bsu cmaps if needed
        cmaps = {
            'bsu_green': LinearSegmentedColormap.from_list("bsu_green", ['#ffffff', '#92e3da'], N=100),
            'bsu_red': LinearSegmentedColormap.from_list("bsu_red", ['#ffffff', '#ff3b3b'], N=100),
            'bsu_blue': LinearSegmentedColormap.from_list("bsu_blue", ['#ffffff', '#2437ff'], N=100)
        }
        if cmap in cmaps: cmap = cmaps[cmap]
        
        x = np.array(x); y = np.array(y)
        if self.orientation == 'horizontal':
             px, py = y, x
        else:
             px, py = x, y
        
        # Extent order: xmin, xmax, ymin, ymax
        extent = self._get_extent(half)
        
        return ax.hexbin(px, py, gridsize=gridsize, cmap=cmap, edgecolors=edgecolors, mincnt=mincnt, extent=extent, **kwargs)
