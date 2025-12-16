# Quick Start Guide - Quant Real-time Analytics

## 🚀 Get Started in 3 Steps

### Step 1: Activate Virtual Environment
```powershell
cd D:\realtime analyzer\quant-realtime-analytics
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
streamlit run app.py
```

## 📍 What You'll See

- Dashboard opens at `http://localhost:8501`
- Click "▶️ Start Stream" to begin receiving mock price data
- Real-time metrics display: Price, Volatility, Moving Averages
- Interactive charts update automatically
- Alerts trigger when thresholds are crossed
- Customize alert thresholds in the sidebar

## 📊 Dashboard Features

| Feature | Description |
|---------|-------------|
| **Current Price** | Live BTC/USD price from mock data |
| **Volatility** | 20-bar rolling standard deviation |
| **SMA (20)** | 20-period simple moving average |
| **EMA (20)** | 20-period exponential moving average |
| **Price Chart** | Shows price with SMA(20) and SMA(50) overlays |
| **Returns Chart** | Distribution histogram of returns |
| **Alert Alerts** | Real-time threshold-based alerts |
| **Data Table** | Last 50 data points with timestamps |

## ⚙️ Configuration

Adjust these in the sidebar:
- **Price Change (%)**: Alert when price moves > this %
- **Volatility Warning**: Yellow alert threshold
- **Volatility Critical**: Red alert threshold

## 🔧 Troubleshooting

**Problem**: Streamlit not found
```bash
pip install streamlit==1.32.0
```

**Problem**: Import errors
```bash
# Ensure venv is activated and all dependencies installed
pip install -r requirements.txt
```

**Problem**: Port already in use
```bash
streamlit run app.py --server.port 8502
```

## 📝 Project Files

- `app.py` - Streamlit dashboard (10.5 KB)
- `websocket_client.py` - Mock data generator (4.2 KB)
- `data_store.py` - Data storage with pandas (3.5 KB)
- `analytics.py` - Quantitative calculations (5.3 KB)
- `alerts.py` - Alert management system (6.5 KB)
- `requirements.txt` - Python dependencies
- `README.md` - Full documentation

## 📚 Learn More

See `README.md` for:
- Detailed architecture
- API documentation
- Extension guidelines
- Performance notes

---

**Status**: ✅ All modules compiled and tested successfully!
**Version**: 1.0.0
**Date**: December 2025
