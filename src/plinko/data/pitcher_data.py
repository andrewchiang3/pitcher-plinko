"""
Data fetching module for MLB pitcher statistics
Handles player lookup and pitch data retrieval
"""

from pybaseball import statcast_pitcher, playerid_lookup
import pandas as pd
from typing import Tuple, Optional
from ..utils.constants import remove_accents

class PitcherDataFetcher:
    """
    Handles fetching and processing pitcher data from pybaseball
    """

    def __init__(self):
        """Initialize the data fetcher"""
        pass
    
    def lookup_pitcher(self, first_name: str, last_name: str) -> Optional[pd.DataFrame]:
        """
        Look up a pitcher by name

        Args: 
            first_name: Pitcher's first name
            last_name: Pitcher's last name

        Returns:
            DataFrame with pitcher information or None if not found 
        """
        try:
            player_data = playerid_lookup(last_name, first_name)
            return player_data if not player_data.empty else None
        except Exception as e:
            raise Exception(f"Error looking up pitcher: {str(e)}")
        
    def get_pitcher_id(self, first_name: str, last_name: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Get pitcher's MLB ID and full name

        Args:
            first_name: Pitcher's first name
            last_name: Pitcher's last name

        Returns:
            Tuple of (pitcher_id, full_name) or (None, None) if not found
        """
        player_data = self.lookup_pitcher(first_name, last_name)

        if player_data is None:
            return None, None
        
        pitcher_id = player_data.iloc[0]['key_mlbam']
        pitcher_full_name = (
            f"{player_data.iloc[0]['name_first'].title()} "
            f"{player_data.iloc[0]['name_last'].title()}"
        )

        return int(pitcher_id), pitcher_full_name
    
    def fetch_pitch_data(
            self,
            pitcher_id: int,
            start_date: str,
            end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch pitch-by-pitch data for a pitcher

        Args:
            pitcher_id: MLB player id
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in formal 'YYYY-MM-DD'

        Returns:
            DataFrame with pitch data or None if no data found
        """
        try:
            data = statcast_pitcher(start_date, end_date, pitcher_id)
            return data if not data.empty else None
        except Exception as e:
            raise Exception(f"Error fetching pitch data: {str(e)}")
        
    def process_pitch_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw pitch data into format needed for visualization

        Args:
            raw_data: Raw statcast data

        Returns:
            Processed DataFrame with count column added
        """
        # Sort by game, at-bat, and pitch number
        data_sorted = raw_data.sort_values(
            by=['game_date', 'at_bat_number', 'pitch_number']
        )

        # Select relevant columns
        pitch_data = data_sorted[[
            'balls', 'strikes', 'pitch_type', 'release_speed',
            'events', 'description', 'game_date',
            'at_bat_number', 'pitch_number'
        ]].copy()

        # Create count column
        pitch_data['count'] = (
            pitch_data['balls'].astype(str) + '-' + pitch_data['strikes'].astype(str)
        )

        return pitch_data
    
    @staticmethod
    def get_all_pitchers() -> pd.DataFrame:
        """
        Get a list of all MLB pitchers from pybaseball
        This is cached to avoid repeated lookups

        Returns:
            DataFrame with all pitcher information
        """
        try:
            from pybaseball import chadwick_register
            players = chadwick_register()

            players = players[players['key_mlbam'].notna()].copy()

            players['full_name'] = (
                players['name_first'].str.title() + ' ' +
                players['name_last'].str.title()
            )

            # Create (accent-free) columns for searching
            players['full_name_normalized'] = players['full_name'].apply(remove_accents).str.lower()

            players = players.sort_values(['name_last', 'name_first'])

            return players
        except Exception as e:
            raise Exception(f"Error fetching pitcher list: {str(e)}")
        
    @staticmethod
    def search_pitchers(search_term: str, all_pitchers: pd.DataFrame, limit: int = 50) -> list:
        """
        Search for pitchers by name

        Args:
            search_term: Name to search for
            all_pitchers: DataFrame of all pitchers
            limit: Maximum number of results to return
        
        Returns:
            List of matching pitcher names
        """
        if not search_term:
            return []
        
        search_term = search_term.lower()

        # Search in both first and last names
        mask = (
            all_pitchers['name_first'].str.lower().str.contains(search_term, na=False) |
            all_pitchers['name_last'].str.lower().str.contains(search_term, na=False) |
            all_pitchers['full_name'].str.lower().str.contains(search_term, na=False)
        )
        
        matches = all_pitchers[mask]['full_name'].unique().tolist()
        
        return matches[:limit]
    
    def get_processed_data(
            self,
            first_name: str,
            last_name: str,
            year: int
    ) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
        """
        Main method to get all processed data for a pitcher

        Args:
            first_name: Pitcher's first name
            last_name: Pitcher's last name
            year: Season year

        Returns:
            Tuple of (processed_data, pitcher_name, error_message)
            If successful: (DataFrame, name, None)
            If failed: (None, None, error_message)
        """
        try:
            # Look up pitcher
            pitcher_id, pitcher_name = self.get_pitcher_id(first_name, last_name)

            if pitcher_id is None:
                return None, None, f"No pitcher found with name {first_name} {last_name}"
            
            # Fetch data
            start_date = f"{year}-03-01"
            end_date = f"{year}-10-01"
            raw_data = self.fetch_pitch_data(pitcher_id, start_date, end_date)

            if raw_data is None:
                return None, None, f"No pitch data found for {pitcher_name} in {year}"

            # Process data
            processed_data = self.process_pitch_data(raw_data)

            return processed_data, pitcher_name, None
        
        except Exception as e:
            return None, None, str(e) 