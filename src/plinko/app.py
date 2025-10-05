"""
Main Streamlit application for MLB Plinko Chart Generator
Provides UI for searching pitchers and generating visualizations
"""

import streamlit as st
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from plinko.data.pitcher_data import PitcherDataFetcher
from plinko.visualization.plinko_chart import create_plinko_chart
from plinko.utils.constants import AVAILABLE_SEASONS

class PlinkoApp:
    """
    Main application class for the Plinko Chart Generator
    """

    def __init__(self):
        """Initialize the application"""
        self.data_fether = PitcherDataFetcher()
        self._setup_page()

    def _setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title = "MLB Plinko Chart",
            layout = "wide",
            initial_sidebar_state = "expanded"
        )

    def _render_header(self):
        """Render the main header"""
        st.title("MLB Pitcher Plinko Chart Generator")
        st.write("Visuallize pitch distribution by count for any MLB pitcher")

    def _render_sidebar(self):
        """
        Render sidebar with pitcher search inputs

        Returns:
            Tuple of (first_name, last_name, year, generate_clicked)
        """
        st.sidebar.header("Pitcher Search")

        # Name inputs
        col1, col2 = st.sidebar.columns(2)
        with col1:
            first_name = st.text_input("First Name", value = "")
        with col2:
            last_name = st.text_input("Last Name", value = "")

        # Season selector
        year = st.sidebar.selectbox(
            "Season",
            AVAILABLE_SEASONS,
            index = 0
        )

        # Generate button
        generate_clicked = st.sidebar.button("Generate Chart", type = "primary")

        return first_name, last_name, year, generate_clicked
    
    def _render_chart(self, first_name: str, last_name: str, year: int):
        """
        Fetch data and render the plinko chart

        Args:
            first_name = Pitcher's first name
            last_name: Pitcher's last name
            year: Season year
        """
        with st.spinner(f"Fetching data for {first_name} {last_name}..."):
            # Fetch and process data
            pitch_data, pitcher_name, error = self.data_fether.get_processed_data(
                first_name, last_name, year
            )

            # Handle errors
            if error:
                st.error(error)
                st.write("Please check the pitcher name and try again.")
                return
            
            # Generate and display chart
            fig = create_plinko_chart(
                pitch_data,
                pitcher_name = f"{pitcher_name} ({year})"
            )
            st.pyplot(fig)

            # Display summary statistics
            self._render_summary_stats(pitch_data)

    def _render_summary_stats(self, pitch_data):
        """
        Render summary statistics below the chart

        Args:
            pitch_data: Processed pitch data
        """
        st.subheader("Pitch Arsenal Summary")

        pitch_counts = pitch_data['pitch_type'].value_counts()

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(pitch_counts, use_container_width = True)

        with col2:
            st.metric("Total Pitches", len(pitch_data))
            st.metric("Pitch Types", len(pitch_counts))

    def run(self):
        """Main application run method"""
        # Render header
        self._render_header()

        # Render sidebar and get inputs
        first_name, last_name, year, generate_clicked = self._render_sidebar()

        # Generate chart if button clicked
        if generate_clicked:
            self._render_chart(first_name, last_name, year)

    def main():
        """Application entry point"""
        app = PlinkoApp()
        app.run()

    if __name__ == "__main__":
        main()
