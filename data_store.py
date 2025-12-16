"""
Data storage and management module.
Stores incoming tick data in memory using pandas DataFrame.
Provides functions to retrieve latest and historical data.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from collections import deque


class DataStore:
    """In-memory data storage for tick data with efficient retrieval."""
    
    def __init__(self, max_records: int = 10000):
        """
        Initialize data store.
        
        Args:
            max_records: Maximum number of records to keep in memory
        """
        self.max_records = max_records
        self.data = deque(maxlen=max_records)  # Circular buffer
        self.df = pd.DataFrame()  # DataFrame for analytics
        
    def add_tick(self, tick_data: Dict) -> None:
        """
        Add a new tick to the data store.
        
        Args:
            tick_data: Dictionary with keys: symbol, timestamp, price, volume
        """
        self.data.append(tick_data)
        # Update DataFrame for efficient analytics
        self.df = pd.DataFrame(list(self.data))
        
        # Convert timestamp to datetime if it exists
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            
    def get_latest(self, n: int = 1) -> pd.DataFrame:
        """
        Get the latest n ticks.
        
        Args:
            n: Number of latest ticks to retrieve
            
        Returns:
            DataFrame with latest n ticks
        """
        if len(self.df) == 0:
            return pd.DataFrame()
        return self.df.tail(n).copy()
    
    def get_historical(self, minutes: int = 60) -> pd.DataFrame:
        """
        Get historical data for the last n minutes.
        
        Args:
            minutes: Number of minutes of historical data
            
        Returns:
            DataFrame with historical data
        """
        if len(self.df) == 0 or 'timestamp' not in self.df.columns:
            return pd.DataFrame()
            
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        mask = self.df['timestamp'] >= cutoff_time
        return self.df[mask].copy()
    
    def get_all(self) -> pd.DataFrame:
        """
        Get all stored data.
        
        Returns:
            DataFrame with all stored data
        """
        return self.df.copy() if len(self.df) > 0 else pd.DataFrame()
    
    def get_latest_price(self) -> Optional[float]:
        """
        Get the most recent price.
        
        Returns:
            Latest price or None if no data
        """
        if len(self.df) == 0:
            return None
        return self.df['price'].iloc[-1]
    
    def get_price_range(self, minutes: int = 60) -> Dict[str, float]:
        """
        Get price range (min, max) for historical period.
        
        Args:
            minutes: Time period in minutes
            
        Returns:
            Dictionary with 'min' and 'max' prices
        """
        hist_data = self.get_historical(minutes)
        if len(hist_data) == 0:
            return {'min': None, 'max': None}
        
        return {
            'min': hist_data['price'].min(),
            'max': hist_data['price'].max()
        }
    
    def clear(self) -> None:
        """Clear all stored data."""
        self.data.clear()
        self.df = pd.DataFrame()
