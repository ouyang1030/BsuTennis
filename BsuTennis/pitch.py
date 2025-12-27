
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
    """
    
    
    def __init__(self, court_type='doubles', line_color='white', pitch_color='#7ba6b6',
                 linewidth=2, axis=False, label=False, tick=False, orientation='horizontal', half=False, theme=None):
        
        if theme is not None and theme in THEMES:
            t = THEMES[theme]
            if 'line_color' in t: line_color = t['line_color']
            if 'pitch_color' in t: pitch_color = t['pitch_color']
            
        super().__init__(court_type=court_type, line_color=line_color, pitch_color=pitch_color,
                         linewidth=linewidth, axis=axis, label=label, tick=tick, orientation=orientation, half=half)
    
    def __repr__(self):
        return f"TennisCourt(court_type={self.court_type}, orientation={self.orientation}, half={self.half})"

Pitch = TennisCourt

# Alias for compatibility if needed, or if user expected 'Pitch' style naming?
# But TennisCourt is more precise.
