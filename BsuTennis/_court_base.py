
import numpy as np
from .dimension import (LENGTH, WIDTH_SINGLES, WIDTH_DOUBLES, 
                        SERVICE_LINE_DISTANCE, ALLEY_WIDTH, HALF_LENGTH)

class BaseCourt:
    """
    The BaseCourt class handles the logical dimensions and geometry of the tennis court.
    It mimics mplsoccer's _pitch_base.py by abstracting geometry from plotting.
    
    Parameters
    ----------
    court_type : str, default 'doubles'
        'singles' or 'doubles'.
    orientation : str, default 'vertical'
        'vertical' (length along Y) or 'horizontal' (length along X).
    half : bool, default False
        If True, defines geometry for only one side of the net (usually Bottom/Left).
    """
    
    def __init__(self, court_type='doubles', orientation='vertical', half=False, **kwargs):
        self.court_type = court_type
        self.orientation = orientation
        self.half = half
        
        # Dimensions
        self.length = LENGTH
        self.width = WIDTH_DOUBLES if court_type == 'doubles' else WIDTH_SINGLES
        
        # Limits (assuming Center Origin (0,0) at Net Center)
        # This matches the 'transform_coordinate' target system.
        if half:
            self.y_min = 0
            self.y_max = HALF_LENGTH
        else:
            self.y_min = -HALF_LENGTH
            self.y_max = HALF_LENGTH
            
        self.x_min = -self.width / 2
        self.x_max = self.width / 2
        
        # Aspect Ratio & Extent calculation
        if orientation == 'horizontal':
            # Swap Dimensions logic
            # x is length, y is width
            if half:
                self.extent = [0, HALF_LENGTH, -self.width/2, self.width/2]
            else:
                self.extent = [-HALF_LENGTH, HALF_LENGTH, -self.width/2, self.width/2]
            self.aspect = self.width / (HALF_LENGTH if half else LENGTH)
        else:
            # Vertical
            # x is width, y is length
            if half:
                self.extent = [-self.width/2, self.width/2, 0, HALF_LENGTH]
            else:
                self.extent = [-self.width/2, self.width/2, -HALF_LENGTH, HALF_LENGTH]
            self.aspect = (HALF_LENGTH if half else LENGTH) / self.width

        # Specific Lines (Geometry helper)
        self.service_line_dist = SERVICE_LINE_DISTANCE
        self.alley = ALLEY_WIDTH if court_type == 'doubles' else 0

    def contains(self, x, y):
        """
        Check if point (x,y) contains within court boundaries.
        """
        # Logic depends on orientation? 
        # BaseCourt usually handles Standardized Coordinates (Vertical).
        # We assume x, y are in Standard Vertical geometry?
        # If user passes raw horizontal data, they must transform first.
        return (x >= self.x_min) & (x <= self.x_max) & (y >= self.y_min) & (y <= self.y_max)
