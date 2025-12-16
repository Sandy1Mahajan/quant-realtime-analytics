"""
WebSocket client for streaming real-time market data.
Connects to Binance WebSocket for live crypto price data.
Falls back to mock data if connection fails.
"""

import asyncio
import json
from datetime import datetime
from typing import Callable, Optional
import random
import websockets


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


class BinanceWebSocketClient:
    """Real WebSocket client that connects to Binance for live crypto data."""
    
    def __init__(self, symbol: str = "btcusdt", interval: float = 1.0):
        """
        Initialize Binance WebSocket client.
        
        Args:
            symbol: Binance trading pair (lowercase, e.g., "btcusdt", "ethusdt")
            interval: Update interval in seconds (note: Binance sends real-time data)
        """
        self.symbol = symbol
        self.interval = interval
        self.is_connected = False
        # Binance testnet URL
        self.url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        
    async def connect(self):
        """Establish WebSocket connection to Binance."""
        self.is_connected = True
        print(f"[Binance WebSocket] Connecting to {self.symbol}...")
        
    async def disconnect(self):
        """Close WebSocket connection."""
        self.is_connected = False
        print(f"[Binance WebSocket] Disconnected from {self.symbol}")
        
    async def stream_data(self, callback: Callable):
        """
        Stream live price data from Binance.
        
        Args:
            callback: Async function to process each data point
        """
        await self.connect()
        
        try:
            async with websockets.connect(self.url) as websocket:
                print(f"[Binance WebSocket] Connected successfully to {self.symbol}")
                
                while self.is_connected:
                    try:
                        # Receive message from Binance
                        message = await asyncio.wait_for(websocket.recv(), timeout=30)
                        data = json.loads(message)
                        
                        # Parse Binance trade data
                        tick_data = {
                            "symbol": self.symbol.upper(),
                            "timestamp": datetime.fromtimestamp(data['T'] / 1000).isoformat(),
                            "price": float(data['p']),  # p = price
                            "volume": float(data['q'])   # q = quantity
                        }
                        
                        # Call callback with parsed data
                        await callback(tick_data)
                        
                        # Optional: throttle updates
                        await asyncio.sleep(self.interval)
                        
                    except asyncio.TimeoutError:
                        print("[Binance WebSocket] Timeout waiting for data")
                    except json.JSONDecodeError:
                        print("[Binance WebSocket] Failed to parse message")
                    except Exception as e:
                        print(f"[Binance WebSocket] Error: {e}")
                        
        except Exception as e:
            print(f"[Binance WebSocket] Connection error: {e}")
            print("[Binance WebSocket] Falling back to mock data...")
            # Fall back to mock data on connection failure
            mock_client = MockWebSocketClient(symbol=self.symbol.upper())
            await mock_client.stream_data(callback)
        finally:
            await self.disconnect()


def get_websocket_client(use_mock: bool = True, symbol: str = "BTC/USD") -> object:
    """
    Factory function to get WebSocket client.
    
    Args:
        use_mock: Use mock data if True, else real Binance WebSocket
        symbol: Trading pair symbol
        
    Returns:
        WebSocket client instance (Mock or Binance)
    """
    if use_mock:
        return MockWebSocketClient(symbol=symbol, interval=1.0)
    else:
        # Convert symbol format: "BTC/USD" -> "btcusdt"
        symbol_binance = symbol.split('/')[0].lower() + "usdt"
        return BinanceWebSocketClient(symbol=symbol_binance, interval=0.5)
