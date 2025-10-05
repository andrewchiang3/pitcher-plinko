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
            pitch_type_counts = count_pitches['pitch_type'].value_counts()
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
    
    def _draw_count_node(self, ax, count: str, position: Tuple[float, float]):
        """
        Draw a count node (pie chart) on the chart 

        Args:
            ax: Matplotlib axis
            count: Count string (e.g., '0-0')
            position: (x, y) coordinates
        """
        x, y = position
        pie_radius = CHART_CONFIG['pie_radius']
        
        # If no data for this count, draw empty circle
        if count not in self.count_data or len(self.count_data[count]) == 0:
            circle = plt.Circle(
                (x, y), pie_radius,
                color = 'lightgray',
                fill = True,
                alpha = 0.3,
                zorder = 1
            )
            ax.add_patch(circle)
            ax.text(
                x, y, count,
                ha = 'center', va = 'center',
                fontsize = 10, fontweight = 'bold',
                zorder = 3
            )
            return
        
        # Get pitch type data for this count
        pitch_types = self.count_data[count]
        total_pitches = pitch_types.sum()

        # Draw pie chart wedges
        start_angle = 90
        for pitch_type, count_val in pitch_types.items():
            angle = 360 * (count_val / total_pitches)
            color = PITCH_COLORS.get(pitch_type, '#cccccc')

            wedge = Wedge(
                (x, y), pie_radius,
                start_angle, start_angle + angle,
                facecolor = color,
                edgecolor = 'white',
                linewidth = 2,
                zorder = 2
            )
            ax.add_patch(wedge)
            start_angle += angle

        # Draw inner white circle (donut chart effect)
        inner_radius = pie_radius * CHART_CONFIG['inner_circle_ratio']
        inner_circle = plt.Circle(
            (x, y), inner_radius,
            color = 'white',
            zorder = 3
        )
        ax.add_patch(inner_circle)

        # Add count label in center
        ax.text(
            x, y, count,
            ha = 'center', va = 'center',
            fontsize = 9, fontweight = 'bold',
            zorder = 4
        )

        # Add pitch count below node
        ax.text(
            x, y - pie_radius - 0.15,
            f'n={int(total_pitches)}',
            ha = 'center', va = 'top',
            fontsize = 8,
            zorder = 4
        )

    def _draw_connecting_lines(self, ax):
        """
        Draw lines connecting count nodes
        Line thickness represents frequency of transitions

        Args:
            ax: Matplotlib axis
        """
        if not self.flow_counts:
            return
        
        max_flow = max(self.flow_counts.values())
        min_width = CHART_CONFIG['min_line_width']
        max_width = CHART_CONFIG['max_line_width']

        for start_count, end_count in COUNT_TRANSITIONS:
            if start_count in COUNT_POSITIONS and end_count in COUNT_POSITIONS:
                x1, y1 = COUNT_POSITIONS[start_count]
                x2, y2 = COUNT_POSITIONS[end_count]
                transition = (start_count, end_count)
                flow_count = self.flow_counts.get(transition, 0)

                if flow_count > 0:
                    # Scale line width based on flow
                    line_width = min_width + (flow_count / max_flow) * (max_width - min_width)

                    ax.plot(
                        [x1, x2], [y1, y2],
                        'k-',
                        alpha = CHART_CONFIG['line_alpha'],
                        linewidth = line_width,
                        zorder = 0
                    )

    def _create_legend(self, ax):
        """
        Create legend showing pitch types and counts

        Args:
            ax: Matplotlib axis
        """
        legend_elements = []

        # Get pitch types that were actually used
        pitch_counts = self.pitch_data['pitch_type'].value_counts()

        # Create legend entry for each pitch type
        for pitch_type in pitch_counts.index:
            if pitch_type in PITCH_COLORS and pd.notna(pitch_type):
                count = pitch_counts.get(pitch_type, 0)
                label = f"{PITCH_NAMES.get(pitch_type, pitch_type)} ({int(count)})"
                patch = patches.Patch(color = PITCH_COLORS[pitch_type], label = label)
                legend_elements.append(patch)

        # Add legend to chart
        num_pitches = len(legend_elements)
        ax.legend(
            handles = legend_elements,
            loc = 'lower center',
            bbox_to_anchor = (0.5, -0.15),
            fontsize = 11,
            ncol = num_pitches,
            frameon = False
        )

    def generate_chart(self):
        """
        Generate the complete plinko chart

        Returns:
            Matplotlib figure object
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize = CHART_CONFIG['figsize'])
        ax.set_xlim(CHART_CONFIG['xlim'])
        ax.set_ylim(CHART_CONFIG['ylim'])
        ax.set_aspect('equal')
        ax.axis('off')

        # Draw connecting lines (behind nodes)
        self._draw_connecting_lines(ax)

        # Draw count nodes (pie charts)
        for count, position in COUNT_POSITIONS.items():
            self._draw_count_node(ax, count, position)

        # Add legend
        self._create_legend(ax)

        # Add title
        total_pitches = len(self.pitch_data)
        plt.title(
            f'{self.pitcher_name} - Pitch Distribution by Count\n'
            f'Total Pitches: {total_pitches}',
            fontsize = 16,
            fontweight = 'bold',
            pad = 20
        )

        plt.tight_layout()
        return fig
    

def create_plinko_chart(pitch_data: pd.DataFrame, pitcher_name: str = "Pitcher"):
        """
        Convenience function to create a plinko chart

        Args:
            pitch_data: Processed pitch data
            pitcher_name: Name to display on chart
        
        Returns:
            Matplotlib figure
        """
        generator = PlinkoChartGenerator(pitch_data, pitcher_name)
        return generator.generate_chart()