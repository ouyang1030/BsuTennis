
from ._court_base import BaseCourt
from ._court_plot import CourtPlotMixin
from .theme import THEMES

class TennisCourt(BaseCourt, CourtPlotMixin):
    """
    Tennis Court Class.
    
    Parameters
    ----------
    court_type : str, default 'doubles'
        The type of court to draw. Options: 'doubles', 'singles'.
    line_color : str, default 'white'
        The color of the lines.
    pitch_color : str, default '#7ba6b6'
        The background color of the court.
    linewidth : float, default 2
        The width of the lines.
    axis : bool, default False
        Whether to draw the axis.
    label : bool, default False
        Whether to label the court.
    tick : bool, default False
        Whether to show ticks.
    orientation : str, optional
        Court orientation: 'horizontal' or 'vertical'.
        If None, defaults to 'horizontal' for full court, 'vertical' for half court.
    half : bool, default False
        Whether to draw only half court.
    theme : str, optional
        Color theme: 'bsu', 'hard', 'clay', 'grass', 'dark', 'light'.
    """
    
    
    def __init__(self, court_type='doubles', line_color='white', pitch_color='#7ba6b6',
                 linewidth=2, axis=False, label=False, tick=False, orientation=None, half=False, theme=None):
        
        # Smart default: full court -> horizontal, half court -> vertical
        if orientation is None:
            orientation = 'vertical' if half else 'horizontal'
        
        if theme is not None and theme in THEMES:
            t = THEMES[theme]
            if 'line_color' in t: line_color = t['line_color']
            if 'pitch_color' in t: pitch_color = t['pitch_color']
            
        # Initialize Geometry (BaseCourt)
        BaseCourt.__init__(self, court_type=court_type, orientation=orientation, half=half)
        
        # Style Attributes (For CourtPlotMixin)
        self.line_color = line_color
        self.pitch_color = pitch_color
        self.linewidth = linewidth
        self.axis = axis
        self.label = label
        self.tick = tick
    
    def __repr__(self):
        return f"TennisCourt(court_type={self.court_type}, orientation={self.orientation}, half={self.half})"

