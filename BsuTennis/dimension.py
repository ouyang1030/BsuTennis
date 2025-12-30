
"""
Tennis Court Dimensions (in meters)
Top-Left Origin (Data) vs Center Origin (Plotting) is handled in stats/base.
Here we define physical properties.
"""

# Standard Dimensions (ITF)
LENGTH = 23.77
WIDTH_SINGLES = 8.23
WIDTH_DOUBLES = 10.97

HALF_LENGTH = LENGTH / 2
HALF_WIDTH_SINGLES = WIDTH_SINGLES / 2
HALF_WIDTH_DOUBLES = WIDTH_DOUBLES / 2

SERVICE_LINE_DISTANCE = 6.40  # From Net
BASELINE_TO_SERVICE_LINE = 5.485 # (11.885 - 6.40)

ALLEY_WIDTH = (WIDTH_DOUBLES - WIDTH_SINGLES) / 2

# For plotting, we usually define a bounding box slightly larger
COURT_LENGTH_EXTENDED = LENGTH + 4 # 2m runoff
COURT_WIDTH_EXTENDED = WIDTH_DOUBLES + 4 # 2m runoff
