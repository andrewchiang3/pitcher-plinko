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
        self.data_fetcher = PitcherDataFetcher()
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
            Tuple of (pitcher_id, pitcher_display_name, year, generate_clicked)
        """
        st.sidebar.header("Pitcher Search")
        
        # Load pitcher list (cached)
        with st.spinner("Loading pitcher database..."):
            all_pitchers = self._get_cached_pitchers()
        
        # Get all pitcher names as a list
        from plinko.utils.constants import remove_accents
        import pandas as pd
        
        pitcher_names_with_duplicates = []
        for name in all_pitchers['full_name'].unique():
            # Skip NaN values
            if pd.notna(name):
                pitcher_names_with_duplicates.append(name)  # Original with accents
                normalized = remove_accents(name)
                # Only add normalized version if it's different
                if normalized != name:
                    pitcher_names_with_duplicates.append(normalized)
        
        # Remove duplicates and sort
        pitcher_names = sorted(list(set(pitcher_names_with_duplicates)))
        
        # Add empty option at the start
        pitcher_names.insert(0, "")
        
        # Searchable selectbox - type to filter!
        selected_pitcher = st.sidebar.selectbox(
            "Search and Select Pitcher",
            options=pitcher_names,
            index=0,
            help="Start typing to filter pitchers, then select from dropdown"
        )
        
        # Get the pitcher ID and clean name
        pitcher_id = None
        pitcher_display_name = None
        
        if selected_pitcher:
            # Remove birth year/debut info: "Luis Castillo (b.1992, debut 2017)" -> "Luis Castillo"
            clean_name = selected_pitcher.split("(")[0].strip()
            
            # Find the pitcher in the dataframe to get their ID
            match = all_pitchers[all_pitchers['full_name'] == selected_pitcher]
            
            if not match.empty:
                pitcher_id = int(match.iloc[0]['key_mlbam'])
                pitcher_display_name = clean_name
        
        # Season selector
        year = st.sidebar.selectbox(
            "Season",
            AVAILABLE_SEASONS,
            index = 0
        )
        
        # Generate button
        generate_clicked = st.sidebar.button("Generate Chart", type="primary")
        
        return pitcher_id, pitcher_display_name, year, generate_clicked
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def _get_cached_pitchers(_self):
        """
        Get cached list of all pitchers
        The underscore in _self prevents Streamlit from hashing the class instance
        """
        return PitcherDataFetcher.get_all_pitchers()
    
    def _render_chart(self, first_name: str, last_name: str, year: int):
        """
        Fetch data and render the plinko chart

        Args:
            first_name: Pitcher's first name
            last_name: Pitcher's last name
            year: Season year
        """
        with st.spinner(f"Fetching data for {first_name} {last_name}..."):
            # Debug: Show what we're searching for
            st.info(f"Searching for: First='{first_name}', Last='{last_name}', Year={year}")
            
            # Fetch and process data
            pitch_data, pitcher_name, error = self.data_fetcher.get_processed_data(
                first_name, last_name, year
            )
            
            # Handle errors
            if error:
                st.error(error)
                st.write("Please check the pitcher name and try again.")
                # Debug: Show the exact error
                with st.expander("Debug Info"):
                    st.write(f"First name used: '{first_name}'")
                    st.write(f"Last name used: '{last_name}'")
                    st.write(f"Year: {year}")
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

    def _render_chart_by_id(self, pitcher_id: int, pitcher_name: str, year: int):
        """
        Fetch data and render the plinko chart using pitcher ID
        
        Args:
            pitcher_id: MLB pitcher ID
            pitcher_name: Display name for the pitcher
            year: Season year
        """
        with st.spinner(f"Fetching data for {pitcher_name}..."):
            # Fetch data directly by ID
            start_date = f"{year}-03-01"
            end_date = f"{year}-10-01"
            
            try:
                raw_data = self.data_fetcher.fetch_pitch_data(pitcher_id, start_date, end_date)
                
                if raw_data is None:
                    st.error(f"No pitch data found for {pitcher_name} in {year}")
                    return
                
                # Process data
                pitch_data = self.data_fetcher.process_pitch_data(raw_data)
                
                # Generate and display chart
                fig = create_plinko_chart(
                    pitch_data,
                    pitcher_name=f"{pitcher_name} ({year})"
                )
                st.pyplot(fig)
                
                # Display summary statistics
                self._render_summary_stats(pitch_data)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

    def run(self):
        """Main application run method"""
        # Render header
        self._render_header()

        # Render sidebar and get inputs
        pitcher_id, pitcher_display_name, year, generate_clicked = self._render_sidebar()

        # Generate chart if button clicked
        if generate_clicked:
            if pitcher_id:
                self._render_chart_by_id(pitcher_id, pitcher_display_name, year)
            else:
                st.warning("Please select a pitcher first")

def main():
    """Application entry point"""
    app = PlinkoApp()
    app.run()

if __name__ == "__main__":
    main()
