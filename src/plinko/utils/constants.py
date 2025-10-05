"""
Constants for MLB Plinko Chart
Contains pitch type definitions, colors, and chart layout configurations
"""

# Pitch type color mappings
PITCH_COLORS = {
    'FF': '#d22d49',  # Four-seam fastball - red
    'SI': '#c14a09',  # Sinker - orange
    'FC': '#933f2c',  # Cutter - brown
    'SL': '#ebc51d',  # Slider - yellow
    'CU': '#00d1ed',  # Curveball - cyan
    'CH': '#1DBE3A',  # Changeup - green
    'FS': '#13bb6b',  # Splitter - teal
    'KC': '#3bacb6',  # Knuckle curve - blue
    'ST': '#f598ce',  # Sweeper - pink
    'SV': '#ea7125',  # Slurve - orange
}

# Full pitch type names for display
PITCH_NAMES = {
    'FF': '4-Seam FB',
    'SI': 'Sinker',
    'FC': 'Cutter',
    'SL': 'Slider',
    'CU': 'Curveball',
    'CH': 'Changeup',
    'FS': 'Splitter',
    'KC': 'Kunckle Curve',
    'ST': 'Sweeper',
    'SV':  'Slurve'
}

# Count positions on the plinko chart (x, y coordinates)
COUNT_POSITIONS = {
    '0-0': (1.5, 4),
    '1-0': (2.75, 3.25),
    '0-1': (0.25, 3.25),
    '2-0': (3.5, 2.5),
    '1-1': (1.5, 2.5),
    '0-2': (-0.5, 2.5),
    '3-0': (3.5, 1.5),
    '2-1': (1.5, 1.5),
    '1-2': (-0.5, 1.5),
    '3-1': (2.75, 0.5),
    '2-2': (0.25, 0.5),
    '3-2': (1.5, 0),
}

# Valid count transitions (representing possible pitch outcomes)
COUNT_TRANSITIONS = [
    ('0-0', '1-0'), ('0-0', '0-1'),
    ('1-0', '2-0'), ('1-0', '1-1'), 
    ('0-1', '1-1'), ('0-1', '0-2'),
    ('2-0', '3-0'), ('2-0', '2-1'), 
    ('1-1', '2-1'), ('1-1', '1-2'),
    ('0-2', '1-2'),
    ('3-0', '3-1'), 
    ('2-1', '3-1'), ('2-1', '2-2'), 
    ('1-2', '2-2'),
    ('3-1', '3-2'), ('2-2', '3-2')
]

# Chart configuration
CHART_CONFIG = {
    'figsize': (20, 10),
    'xlim': (-1, 5),
    'ylim': (-1, 5),
    'pie_radius': 0.25,
    'inner_circle_ratio': 0.5,
    'min_line_width': 1,
    'max_line_width': 20,
    'line_alpha': 0.4,
}

# Get start and end dates for a baseball season
def get_season_dates(year):
    return f"{year}-03-01", f"{year}-10-01"

# Available seasons
AVAILABLE_SEASONS = [2025, 2024, 2023, 2022, 2021, 2020]

import unicodedata
import pandas as pd

def remove_accents(text: str) -> str:
    """
    Remove accents from unicode string
    
    Example: 'José' -> 'Jose', 'Muñoz' -> 'Munoz'
    
    Args:
        text: String with potential accents
        
    Returns:
        String with accents removed
    """
    if pd.isna(text):
        return ""
    
    # Normalize to NFD (decomposed form), then remove combining characters
    nfd = unicodedata.normalize('NFD', str(text))
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')