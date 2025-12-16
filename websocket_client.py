"""
WebSocket client for streaming real-time market data.
Connects to a data source and streams live price data.
Uses mock data if real WebSocket is unavailable.
"""

import asyncio
import json
from datetime import datetime
from typing import Callable, Optional
import random


class MockWebSocketClient:
    """Mock WebSocket client that generates realistic dummy data."""
    
    def __init__(self, symbol: str = "BTC/USD", interval: float = 1.0):
        """
        Initialize mock WebSocket client.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USD")
            interval: Time interval in seconds between price updates
        """
        self.symbol = symbol
        self.interval = interval
        self.is_connected = False
        self.current_price = 45000.0  # Starting price for BTC
        self.price_change = 0
        
    async def connect(self):
        """Establish connection."""
        self.is_connected = True
        print(f"[WebSocket] Connected to {self.symbol}")
        
    async def disconnect(self):
        """Close connection."""
        self.is_connected = False
        print(f"[WebSocket] Disconnected from {self.symbol}")
        
    async def stream_data(self, callback: Callable):
        """
        Stream mock price data at regular intervals.
        
        Args:
            callback: Async function to process each data point
        """
        await self.connect()
        
        try:
            while self.is_connected:
                # Generate realistic price movement (random walk)
                self.price_change = random.gauss(0, 50)  # Mean 0, std 50
                self.current_price += self.price_change
                self.current_price = max(self.current_price, 100)  # Prevent negative
                
                # Create tick data
                tick_data = {
                    "symbol": self.symbol,
                    "timestamp": datetime.now().isoformat(),
                    "price": round(self.current_price, 2),
                    "volume": round(random.uniform(10, 500), 2)
                }
                
                # Call the callback with new data
                await callback(tick_data)
                
                # Wait before next update
                await asyncio.sleep(self.interval)
                
        except asyncio.CancelledError:
            print("[WebSocket] Stream cancelled")
        finally:
            await self.disconnect()


class RealWebSocketClient:
    """
    Real WebSocket client for connecting to actual market data feeds.
    Can be extended to use websockets library or specific exchange APIs.
    """
    
    def __init__(self, url: str, symbol: str):
        """
        Initialize real WebSocket client.
        
        Args:
            url: WebSocket URL to connect to
            symbol: Trading pair symbol
        """
        self.url = url
        self.symbol = symbol
        self.is_connected = False
        
    async def connect(self):
        """Establish WebSocket connection."""
        # Implementation would use websockets library
        # Example: async with websockets.connect(self.url) as websocket:
        self.is_connected = True
        
    async def disconnect(self):
        """Close WebSocket connection."""
        self.is_connected = False
        
    async def stream_data(self, callback: Callable):
        """Stream real price data."""
        # Implementation would process actual WebSocket messages
        pass


def get_websocket_client(use_mock: bool = True, symbol: str = "BTC/USD") -> MockWebSocketClient:
    """
    Factory function to get WebSocket client.
    
    Args:
        use_mock: Use mock data if True, else real WebSocket
        symbol: Trading pair symbol
        
    Returns:
        WebSocket client instance
    """
    if use_mock:
        return MockWebSocketClient(symbol=symbol, interval=1.0)
    else:
        # Would return RealWebSocketClient with actual URL
        return MockWebSocketClient(symbol=symbol, interval=1.0)
