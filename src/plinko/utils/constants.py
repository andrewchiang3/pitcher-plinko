"""
Constants for MLB Plinko Chart
Enhanced with modern color scheme and styling options
"""

# Enhanced pitch type color mappings - more vibrant and distinguishable
PITCH_COLORS = {
    'FF': '#FF4B4B',  # Four-seam fastball - Streamlit red
    'SI': '#FF8C42',  # Sinker - orange
    'FC': '#B85C38',  # Cutter - brown
    'SL': '#FFC914',  # Slider - gold
    'CU': '#00C9FF',  # Curveball - bright cyan
    'CH': '#21C354',  # Changeup - green
    'FS': '#00D4AA',  # Splitter - teal
    'KC': '#4A9EFF',  # Knuckle curve - blue
    'ST': '#FF6EC7',  # Sweeper - pink
    'SV': '#FF7043',  # Slurve - coral
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
    'KC': 'Knuckle Curve',
    'ST': 'Sweeper',
    'SV': 'Slurve'
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

# Enhanced chart configuration with better styling
CHART_CONFIG = {
    'figsize': (18, 9),
    'xlim': (-1, 5),
    'ylim': (-1, 5),
    'pie_radius': 0.28,
    'inner_circle_ratio': 0.5,
    'min_line_width': 1.5,
    'max_line_width': 18,
    'line_alpha': 0.3,
}

# Streamlit theme colors
STREAMLIT_THEME = {
    'light': {
        'background': '#FFFFFF',
        'text': '#262730',
        'secondary_text': '#808495',
        'border': '#E6EBF1',
        'empty_node': '#F0F2F6'
    },
    'dark': {
        'background': '#0E1117',
        'text': '#FAFAFA',
        'secondary_text': '#A3A8B4',
        'border': '#262730',
        'empty_node': '#31333F'
    }
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
    
    nfd = unicodedata.normalize('NFD', str(text))
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')