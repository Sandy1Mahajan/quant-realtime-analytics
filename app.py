"""
Streamlit dashboard for real-time quantitative analytics.
Displays live price updates, analytics charts, and alerts.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import asyncio
from datetime import datetime
import time
from typing import Dict
import random

# Import project modules
from websocket_client import get_websocket_client
from data_store import DataStore
from analytics import QuantAnalytics
from alerts import AlertManager, AlertLevel


# Configure Streamlit
st.set_page_config(
    page_title="Realtime Quant Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .alert-box {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .alert-info { background-color: #e7f3ff; border-left: 4px solid #2196F3; }
    .alert-warning { background-color: #fff3cd; border-left: 4px solid #ffc107; }
    .alert-critical { background-color: #f8d7da; border-left: 4px solid #dc3545; }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'data_store' not in st.session_state:
        st.session_state.data_store = DataStore(max_records=5000)
    if 'alert_manager' not in st.session_state:
        st.session_state.alert_manager = AlertManager()
    if 'use_mock_data' not in st.session_state:
        st.session_state.use_mock_data = True
    if 'ws_client' not in st.session_state:
        st.session_state.ws_client = get_websocket_client(use_mock=st.session_state.use_mock_data, symbol="BTC/USD")
    if 'is_streaming' not in st.session_state:
        st.session_state.is_streaming = False
    if 'stream_task' not in st.session_state:
        st.session_state.stream_task = None
    if 'previous_price' not in st.session_state:
        st.session_state.previous_price = None


async def data_stream_callback(tick_data: Dict):
    """Callback function for processing incoming tick data."""
    # Add to data store
    st.session_state.data_store.add_tick(tick_data)
    
    # Check alerts
    current_price = tick_data['price']
    if st.session_state.previous_price is not None:
        st.session_state.alert_manager.check_price_alert(
            current_price, 
            st.session_state.previous_price
        )
    st.session_state.previous_price = current_price
    
    # Calculate volatility and check volatility alerts
    df = st.session_state.data_store.get_all()
    if len(df) > 10:
        volatility = QuantAnalytics.calculate_volatility(df['price'])
        st.session_state.alert_manager.check_volatility_alert(volatility)


def render_metrics():
    """Render key metrics in columns."""
    df = st.session_state.data_store.get_all()
    
    if len(df) == 0:
        st.info("⏳ Waiting for data...")
        return
    
    metrics = QuantAnalytics.calculate_metrics(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current Price",
            f"${metrics['current_price']:.2f}",
            f"{metrics['price_change_pct']:.2f}%"
        )
    
    with col2:
        st.metric(
            "Volatility",
            f"{metrics['volatility']:.4f}",
            f"Window: 20 bars"
        )
    
    with col3:
        st.metric(
            "SMA (20)",
            f"${metrics['ma_short']:.2f}" if metrics['ma_short'] else "N/A"
        )
    
    with col4:
        st.metric(
            "EMA (20)",
            f"${metrics['ema_short']:.2f}" if metrics['ema_short'] else "N/A"
        )


def render_price_chart():
    """Render interactive price chart."""
    df = st.session_state.data_store.get_all()
    
    if len(df) < 2:
        st.info("Not enough data for chart")
        return
    
    # Create Plotly figure
    fig = go.Figure()
    
    # Add candlestick-like price line
    fig.add_trace(go.Scatter(
        x=df['timestamp'] if 'timestamp' in df.columns else range(len(df)),
        y=df['price'],
        mode='lines',
        name='Price',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Add moving averages
    ma_short = QuantAnalytics.calculate_moving_average(df['price'], 20)
    ma_long = QuantAnalytics.calculate_moving_average(df['price'], 50)
    
    if len(ma_short) > 0:
        fig.add_trace(go.Scatter(
            x=df['timestamp'] if 'timestamp' in df.columns else range(len(df)),
            y=ma_short,
            mode='lines',
            name='SMA (20)',
            line=dict(color='orange', width=1, dash='dash')
        ))
    
    if len(ma_long) > 0:
        fig.add_trace(go.Scatter(
            x=df['timestamp'] if 'timestamp' in df.columns else range(len(df)),
            y=ma_long,
            mode='lines',
            name='SMA (50)',
            line=dict(color='red', width=1, dash='dash')
        ))
    
    fig.update_layout(
        title='Price & Moving Averages',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_returns_chart():
    """Render returns distribution chart."""
    df = st.session_state.data_store.get_all()
    
    if len(df) < 2:
        return
    
    returns = QuantAnalytics.calculate_simple_returns(df['price']) * 100
    
    fig = px.histogram(
        returns,
        nbins=30,
        labels={'value': 'Return (%)', 'count': 'Frequency'},
        title='Distribution of Returns'
    )
    
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_alerts():
    """Render recent alerts."""
    alerts = st.session_state.alert_manager.get_recent_alerts(10)
    
    if len(alerts) == 0:
        st.info("✅ No alerts yet")
        return
    
    st.subheader("Recent Alerts")
    
    for alert in reversed(alerts):
        # Determine CSS class based on level
        if alert.level == AlertLevel.CRITICAL:
            css_class = "alert-critical"
            emoji = "🔴"
        elif alert.level == AlertLevel.WARNING:
            css_class = "alert-warning"
            emoji = "🟡"
        else:
            css_class = "alert-info"
            emoji = "🔵"
        
        # Display alert with HTML
        st.markdown(
            f'<div class="alert-box {css_class}">{emoji} <b>{alert.level.value}</b> - {alert.message}<br><small>{alert.timestamp.strftime("%H:%M:%S")}</small></div>',
            unsafe_allow_html=True
        )


def render_data_table():
    """Render raw data table."""
    df = st.session_state.data_store.get_latest(50)
    
    if len(df) == 0:
        st.info("No data available")
        return
    
    # Format for display
    display_df = df[['symbol', 'timestamp', 'price', 'volume']].copy()
    if 'timestamp' in display_df.columns:
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%H:%M:%S')
    
    st.dataframe(display_df, use_container_width=True)


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("📊 Realtime Quant Analyzer")
    st.markdown("Real-time quantitative analytics dashboard with live price updates and alerts")
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Data source toggle
        st.subheader("Data Source")
        use_real_data = st.checkbox("Use Real Binance Data", value=False)
        if use_real_data != st.session_state.use_mock_data:
            st.session_state.use_mock_data = not use_real_data
            st.session_state.ws_client = get_websocket_client(use_mock=st.session_state.use_mock_data, symbol="BTC/USD")
            if st.session_state.is_streaming:
                st.warning("⚠️ Data source changed. Restart streaming.")
        
        if use_real_data:
            st.info("🔴 Live Binance Data - Real BTCUSDT prices")
        else:
            st.info("📊 Mock Data - Simulated prices for testing")
        
        st.divider()
        
        # Streaming controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start Stream", key="start_btn"):
                st.session_state.is_streaming = True
                st.success("Streaming started!")
        
        with col2:
            if st.button("⏹️ Stop Stream", key="stop_btn"):
                st.session_state.is_streaming = False
                st.info("Streaming stopped")
        
        st.divider()
        
        # Alert thresholds
        st.subheader("Alert Thresholds")
        price_threshold = st.slider(
            "Price Change (%)",
            min_value=0.1,
            max_value=10.0,
            value=2.0,
            step=0.1
        )
        
        vol_threshold = st.slider(
            "Volatility Warning",
            min_value=0.001,
            max_value=0.1,
            value=0.02,
            step=0.001,
            format="%.3f"
        )
        
        vol_critical = st.slider(
            "Volatility Critical",
            min_value=0.01,
            max_value=0.2,
            value=0.05,
            step=0.01,
            format="%.3f"
        )
        
        st.session_state.alert_manager.set_thresholds(
            price_change=price_threshold,
            volatility=vol_threshold,
            volatility_critical=vol_critical
        )
        
        st.divider()
        
        # Statistics
        st.subheader("Statistics")
        df = st.session_state.data_store.get_all()
        st.metric("Records Stored", len(df))
        st.metric("Alerts Generated", len(st.session_state.alert_manager.get_all_alerts()))
    
    # Main content
    # Metrics row
    render_metrics()
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        render_price_chart()
    
    with col2:
        render_returns_chart()
    
    st.divider()
    
    # Alerts section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_alerts()
    
    with col2:
        st.subheader("Recent Data")
        render_data_table()
    
    # Simulate streaming if enabled
    if st.session_state.is_streaming:
        # Mock streaming - add data periodically
        tick_data = {
            "symbol": "BTC/USD",
            "timestamp": datetime.now().isoformat(),
            "price": 45000 + random.gauss(0, 500),
            "volume": round(random.uniform(10, 500), 2)
        }
        
        asyncio.run(data_stream_callback(tick_data))
        
        # Refresh the page
        time.sleep(1)
        st.rerun()


if __name__ == "__main__":
    main()
