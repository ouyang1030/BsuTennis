
import pandas as pd
import numpy as np

def transform_coordinate(x, y):
    """
    Transform raw coordinates (Assuming Top-Left origin or similar) 
    to centered Tennis Court coordinates (Net=0,0).
    Based on 'serve_point.py' logic:
    new_x = x - 5.485
    new_y = 11.885 - y
    """
    new_x = x - 5.485
    new_y = 11.885 - y
    
    # Logic from serve_point.py suggests it flips if y < 0?
    # "if new_y < 0: return -new_x, -new_y"
    # This logic seems to map everything to one side of the court for served points?
    # Yes, for serving visualization, you usually map everything to the "upper" court.
    
    if new_y < 0:
        return -new_x, -new_y
    else:
        return new_x, new_y

def classify_serve_zone(x, y):
    """
    Classify serve landing zone based on coordinates.
    Returns: 1 (Wide), 2 (Body), 3 (T) or combined strings.
    
    From serve_point.py:
    x ranges:
    Left: -4.115 to 0. Divided by 3.
    Right: 0 to 4.115. Divided by 3.
    """
    
    # Constants
    SINGLE_WIDTH = 8.23
    HALF_WIDTH = SINGLE_WIDTH / 2 # 4.115
    SERVICE_LENGTH = 6.4
    THIRD_WIDTH = HALF_WIDTH / 3 # ~1.37
    
    # Check bounds (must be in service box depth)
    # The user logic uses 0 < y <= 6.4.
    # Note: transformed coordinates assume y > 0 is correct for this.
    if not (0 < y <= SERVICE_LENGTH):
        return 'Out' # Too long or at net
        
    # Deuce Court (Right side from server, Left side on plot x < 0?)
    # Wait, server serves diagonally.
    # Deuce serve lands in Left Service Box (x < 0).
    # Ad serve lands in Right Service Box (x > 0).
    
    # User Logic:
    # -4.115 <= x < -8.23/3 (Left Wide?) -> 1
    # -8.23/3 <= x < -4.115/3 (Left Body?) -> 2
    # -4.115/3 <= x <= 0 (Left T?) -> 3
    
    # 0 <= x < 4.115/3 (Right T?) -> 3
    # 4.115/3 <= x < 8.23/3 (Right Body?) -> 2
    # 8.23/3 <= x <= 4.115 (Right Wide?) -> 1
    
    zone = None
    
    # Left Box (Ad Court for receiver, Deuce Court for server)
    if -HALF_WIDTH <= x < -2 * THIRD_WIDTH:
        zone = 'Wide' # Deuce Wide if serve from bottom
    elif -2 * THIRD_WIDTH <= x < -THIRD_WIDTH:
        zone = 'Body' # Deuce Body
    elif -THIRD_WIDTH <= x <= 0:
        zone = 'T'    # Deuce T
        
    # Right Box (Deuce Court for receiver, Ad Court for server)
    elif 0 <= x < THIRD_WIDTH:
        zone = 'T'    # Ad T
    elif THIRD_WIDTH <= x < 2 * THIRD_WIDTH:
        zone = 'Body' # Ad Body
    elif 2 * THIRD_WIDTH <= x <= HALF_WIDTH:
        zone = 'Wide' # Ad Wide
        
    if zone:
        return zone
    else:
        return 'Out' # Too wide

def classify_shot_depth(y, max_length=11.885):
    """
    Classify shot depth (Short, Middle, Long).
    Based on 'draw_moving_bar.py' categories?
    Not explicitly defined there, but usually:
    Short: Service box lines?
    User categories: Short (0-2m), Medium (2-4m), Long (>4m).
    This refers to RUNNING DISTANCE not shot depth.
    
    For landing depth (common in tennis analysis):
    - Service Box (0-6.4m)
    - No Man's Land (6.4-8.23m approx)
    - Deep (8.23-11.89m)
    
    Since user didn't define shot depth logic explicitly in the files I reviewed (except moving distance),
    I will omit this for now to avoid confusion.
    """
    pass
