"""
Analytics and calculation engine.
Computes log returns, volatility, moving averages, and other metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple


class QuantAnalytics:
    """Quantitative analytics engine for market data."""
    
    @staticmethod
    def calculate_log_returns(prices: pd.Series) -> pd.Series:
        """
        Calculate log returns from price series.
        log_return(t) = ln(price(t) / price(t-1))
        
        Args:
            prices: Series of prices
            
        Returns:
            Series of log returns
        """
        if len(prices) < 2:
            return pd.Series(dtype=float)
        
        return np.log(prices / prices.shift(1)).dropna()
    
    @staticmethod
    def calculate_simple_returns(prices: pd.Series) -> pd.Series:
        """
        Calculate simple returns from price series.
        simple_return(t) = (price(t) - price(t-1)) / price(t-1)
        
        Args:
            prices: Series of prices
            
        Returns:
            Series of simple returns
        """
        if len(prices) < 2:
            return pd.Series(dtype=float)
        
        return prices.pct_change().dropna()
    
    @staticmethod
    def calculate_volatility(prices: pd.Series, window: int = 20) -> float:
        """
        Calculate rolling volatility (standard deviation of returns).
        
        Args:
            prices: Series of prices
            window: Rolling window size
            
        Returns:
            Current volatility (annualized if intraday data)
        """
        if len(prices) < window:
            return 0.0
        
        returns = QuantAnalytics.calculate_simple_returns(prices)
        if len(returns) < window:
            return returns.std()
        
        # Rolling std of last 'window' returns
        return returns.tail(window).std()
    
    @staticmethod
    def calculate_moving_average(prices: pd.Series, window: int = 20) -> pd.Series:
        """
        Calculate simple moving average.
        
        Args:
            prices: Series of prices
            window: Window size for moving average
            
        Returns:
            Series of moving average values
        """
        if len(prices) < window:
            return pd.Series(dtype=float)
        
        return prices.rolling(window=window, min_periods=1).mean()
    
    @staticmethod
    def calculate_ema(prices: pd.Series, window: int = 20) -> pd.Series:
        """
        Calculate exponential moving average.
        
        Args:
            prices: Series of prices
            window: Window size for EMA
            
        Returns:
            Series of EMA values
        """
        if len(prices) < window:
            return pd.Series(dtype=float)
        
        return prices.ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def calculate_metrics(df: pd.DataFrame, window_short: int = 20, 
                         window_long: int = 50) -> Dict[str, float]:
        """
        Calculate all key metrics from price data.
        
        Args:
            df: DataFrame with 'price' column and optional 'timestamp'
            window_short: Short moving average window
            window_long: Long moving average window
            
        Returns:
            Dictionary with calculated metrics
        """
        if len(df) == 0 or 'price' not in df.columns:
            return {}
        
        prices = df['price']
        
        # Calculate returns
        log_returns = QuantAnalytics.calculate_log_returns(prices)
        simple_returns = QuantAnalytics.calculate_simple_returns(prices)
        
        # Calculate volatility
        volatility = QuantAnalytics.calculate_volatility(prices)
        
        # Calculate moving averages
        ma_short = QuantAnalytics.calculate_moving_average(prices, window_short)
        ma_long = QuantAnalytics.calculate_moving_average(prices, window_long)
        ema_short = QuantAnalytics.calculate_ema(prices, window_short)
        
        # Get current values
        current_price = prices.iloc[-1] if len(prices) > 0 else 0
        current_ma_short = ma_short.iloc[-1] if len(ma_short) > 0 else None
        current_ma_long = ma_long.iloc[-1] if len(ma_long) > 0 else None
        current_ema_short = ema_short.iloc[-1] if len(ema_short) > 0 else None
        
        # Calculate price changes
        price_change = simple_returns.iloc[-1] * 100 if len(simple_returns) > 0 else 0
        
        return {
            'current_price': round(current_price, 2),
            'price_change_pct': round(price_change, 4),
            'volatility': round(volatility, 6),
            'ma_short': round(current_ma_short, 2) if current_ma_short else None,
            'ma_long': round(current_ma_long, 2) if current_ma_long else None,
            'ema_short': round(current_ema_short, 2) if current_ema_short else None,
            'num_records': len(df),
            'mean_return': round(simple_returns.mean() * 100, 4) if len(simple_returns) > 0 else 0
        }
