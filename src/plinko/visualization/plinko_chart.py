"""
Plinko chart visualization module
Creates Baseball Savant-style plinko charts showing pitch distribution by count
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Wedge
import numpy as np
from typing import Dict, Tuple

from ..utils.constants import (
    PITCH_COLORS,
    PITCH_NAMES,
    COUNT_POSITIONS,
    COUNT_TRANSITIONS,
    CHART_CONFIG
)


class PlinkoChartGenerator:
    """ 
    Genereates plinko-style visualizations of pitcher data
    """

    def __init__(self, pitch_data: pd.DataFrame, pitcher_name: str = "Pitcher"):
        """
        Initialize the chart generator

        Args:
            pitch_data: Processed pitch data with 'count' and 'pitch_type' columns
            pitcher_name: Name to display on chart
        """

        self.pitch_data = pitch_data
        self.pitcher_name = pitcher_name
        self.count_data = self._calculate_count_data()
        self.flow_counts = self._calculate_flow_counts()

    def _calculate_count_data(self) -> Dict[str, pd.Series]:
        """
        Calculate pitch type distribution for each count

        Returns:
            Dictionary mapping count to pitch type counts
        """
        count_data = {}
        for count in COUNT_POSITIONS.keys():
            count_pitches = self.pitch_data[self.pitch_data['count'] == count]
            pitch_type_counts = count_pitches['pitch_type'].value.counts()
            count_data[count] = pitch_type_counts

        return count_data
    
    def _calculate_flow_counts(self) -> Dict[Tuple[str, str], int]:
        """
        Calculate the number of transitions between counts

        Returns:
            Dictionary mapping (start_count, end_count) to transition count
        """
        flow_counts = {}
        transition_set = set(COUNT_TRANSITIONS)

        # Sort data by game, at-bat, and pitch number
        pitch_data_sorted = self.pitch_data.sort_values(
            by = ['game_date', 'at_bat_number', 'pitch_number']
        )

        # Group by at-bat and track transitions
        for (game, at_bat), group in pitch_data_sorted.groupby(['game_date', 'at_bat_number']):
            counts_in_ab = group['count'].tolist()

            # Track each transition within the at-bat
            for i in range(len(counts_in_ab) - 1):
                current_count = counts_in_ab[i]
                next_count = counts_in_ab[i + 1]
                transition = (current_count, next_count)

                if transition in transition_set:
                    flow_counts[transition] = flow_counts.get(transition, 0) + 1

        return flow_counts