
"""
BsuTennis Themes
"""

THEMES = {
    'bsu': {
        'line_color': 'black',
        'pitch_color': None, # Transparent/White
        'zone_color_deuce': 'lightseagreen',
        'zone_color_ad': 'lightseagreen',
        # Colors from logic:
        # BSU Light Blue: #66DCE3
        # BSU Dark Blue: #12237F
        # BSU Light Green: #C5E0B3
    },
    'hard': {
        'line_color': 'white',
        'pitch_color': '#3C638E', # Basic US Open Blue-ish
    },
    'clay': {
        'line_color': 'white',
        'pitch_color': '#CC5500', # Burnt Orange
    },
    'grass': {
        'line_color': 'white',
        'pitch_color': '#4B8B3B', # Grass Green
        'stripe': True #
    },
    'dark': {
        'line_color': '#cfcfcf',
        'pitch_color': '#222222', 
    },
    'light': {
        'line_color': 'black',
        'pitch_color': '#f9f9f9',
    }
}

# Styles mimicking 'visualization.py' and 'serve_point.py'
SCATTER_STYLES = {
    # Events
    'winner_fh': {'facecolor': '#e66868', 'edgecolor': 'black', 'marker': '*', 's': 80, 'linewidths': 0.5, 'alpha': 0.8},
    'forcing_fh': {'facecolor': '#eb8686', 'edgecolor': 'black', 'marker': '^', 's': 40, 'linewidths': 0.5, 'alpha': 0.8},
    
    'winner_bh': {'facecolor': '#556ee6', 'edgecolor': 'black', 'marker': '*', 's': 80, 'linewidths': 0.5, 'alpha': 0.8},
    'forcing_bh': {'facecolor': '#778beb', 'edgecolor': 'black', 'marker': '^', 's': 40, 'linewidths': 0.5, 'alpha': 0.8},
    
    'winner': {'facecolor': '#3ec1d3', 'edgecolor': 'black', 'marker': '*', 's': 80, 'linewidths': 0.5, 'alpha': 0.8},
    'forcing': {'facecolor': '#64cddb', 'edgecolor': 'black', 'marker': '^', 's': 40, 'linewidths': 0.5, 'alpha': 0.8},

    # Errors (from serve_point.py logic)
    'ue': {'facecolor': 'None', 'edgecolor': 'indianred', 'marker': '^', 's': 40, 'linewidths': 1.0},
    'fe': {'facecolor': 'None', 'edgecolor': 'indianred', 'marker': '^', 's': 40, 'linewidths': 1.0},
    
    # Serve
    'ace': {'facecolor': 'None', 'edgecolor': 'indianred', 'marker': '*', 's': 60, 'linewidths': 1.0},
    
    # Generic
    'standard': {'facecolor': 'None', 'edgecolor': 'dimgrey', 'marker': 'o', 's': 30, 'linewidths': 1.0},
    'landing': {'facecolor': 'black', 'edgecolor': 'None', 'marker': 'o', 's': 10, 'alpha': 0.6}
}
