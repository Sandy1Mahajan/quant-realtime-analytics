# 📊 Quant Real-time Analytics

A real-time quantitative analytics platform for market data streaming, analysis, and alert generation. Built with Streamlit, Pandas, and Plotly for interactive financial data visualization.

## Features

✨ **Real-time Data Streaming**
- Mock WebSocket client for continuous price data generation
- Extensible to connect with real market data feeds (crypto, stocks, forex)
- Configurable streaming intervals

📈 **Advanced Analytics**
- Log returns and simple returns calculation
- Rolling volatility computation
- Simple Moving Averages (SMA) and Exponential Moving Averages (EMA)
- Price momentum tracking

🚨 **Intelligent Alerting**
- Price threshold-based alerts
- Volatility-based warnings and critical alerts
- Customizable alert thresholds via UI
- Alert history tracking

📊 **Interactive Dashboard**
- Live price updates with Plotly charts
- Price & moving averages visualization
- Returns distribution histogram
- Real-time data table view
- Responsive UI with Streamlit

## Project Structure

```
quant-realtime-analytics/
├── app.py                  # Streamlit dashboard entry point
├── websocket_client.py     # WebSocket client for data streaming
├── data_store.py           # In-memory data storage with DataFrame
├── analytics.py            # Quantitative analytics engine
├── alerts.py               # Alert generation and management
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── venv/                  # Python virtual environment
```

## File Descriptions

### `app.py`
Main Streamlit application with:
- Dashboard layout with metrics, charts, and alerts
- Session state management
- Interactive controls for streaming and thresholds
- Real-time data visualization

### `websocket_client.py`
Provides:
- `MockWebSocketClient`: Generates realistic dummy price data using random walk
- `RealWebSocketClient`: Template for connecting to actual market data APIs
- Configurable symbols and update intervals

### `data_store.py`
- Circular buffer with max_records limit
- Pandas DataFrame for efficient analytics
- Functions to retrieve latest, historical, and aggregated data
- Price range calculations

### `analytics.py`
Implements quantitative calculations:
- `calculate_log_returns()`: Natural log of price ratios
- `calculate_simple_returns()`: Percentage returns
- `calculate_volatility()`: Rolling standard deviation
- `calculate_moving_average()`: SMA with configurable windows
- `calculate_ema()`: Exponential moving average
- `calculate_metrics()`: All metrics in one call

### `alerts.py`
Alert management system:
- `Alert` class: Individual alert with level, message, value, threshold
- `AlertManager` class: Tracks alerts, manages thresholds, executes callbacks
- Three alert levels: INFO, WARNING, CRITICAL
- Configurable price change and volatility thresholds

## Installation

### 1. Prerequisites
- Python 3.8+
- pip or conda

### 2. Setup Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Streamlit Dashboard
```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### Application Usage

1. **Start Streaming**: Click "▶️ Start Stream" to begin receiving mock data
2. **Configure Alerts**: Adjust thresholds in the sidebar:
   - Price Change (%): Price movement threshold
   - Volatility Warning: Yellow alert level
   - Volatility Critical: Red alert level
3. **View Metrics**: Dashboard displays:
   - Current Price
   - Volatility (20-bar rolling)
   - Short & Long Moving Averages
4. **Monitor Alerts**: Recent alerts appear in real-time
5. **Analyze Data**: Charts update with price and returns distribution

## Technical Details

### Data Flow
```
WebSocket Client → Data Store (DataFrame) → Analytics Engine
                                         ↓
                                    Alert Manager
                                         ↓
                                  Streamlit Dashboard
```

### Dependencies
- **streamlit** (1.32.0): Web framework for dashboard
- **pandas** (2.1.3): Data manipulation and analysis
- **numpy** (1.24.3): Numerical computations
- **plotly** (5.18.0): Interactive visualizations
- **python-dateutil** (2.8.2): Date utilities
- **pytz** (2023.3.post1): Timezone support

## Extending the Project

### Connect Real Market Data
Modify `websocket_client.py` to implement `RealWebSocketClient` with:
- WebSocket connection to exchange APIs (Binance, Coinbase, etc.)
- Message parsing and validation
- Error handling and reconnection logic

### Add More Analytics
Extend `analytics.py` with:
- Bollinger Bands
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- ATR (Average True Range)

### Custom Alerts
Extend `AlertManager` with:
- Pattern recognition alerts
- Correlation-based alerts
- ML-based anomaly detection
- Email/SMS notifications

## Troubleshooting

### Streamlit not found
```bash
pip install streamlit==1.32.0
```

### Import errors
Ensure all modules are in the same directory and virtual environment is activated

### No data appearing
1. Check if "Start Stream" button was clicked
2. Verify venv is activated
3. Check browser console for errors

### Port already in use
```bash
streamlit run app.py --server.port 8502
```

## Performance Notes

- Mock data generation: ~1 data point per second
- Storage limit: 5,000 records in-memory
- Analytics computed on-demand (minimal latency)
- Dashboard updates: Real-time when streaming enabled

## License

Open source project for educational and research purposes.

## Author

Quantitative Analytics Team - December 2025
