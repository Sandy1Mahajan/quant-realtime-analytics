"""
Alert system and notifications module.
Generates alerts when price or volatility thresholds are crossed.
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Alert:
    """Represents a single alert."""
    
    def __init__(self, level: AlertLevel, message: str, value: float, 
                 threshold: float, metric: str):
        """
        Initialize alert.
        
        Args:
            level: Alert severity level
            message: Alert message
            value: Current value that triggered alert
            threshold: Threshold that was crossed
            metric: Name of metric that triggered alert
        """
        self.level = level
        self.message = message
        self.value = value
        self.threshold = threshold
        self.metric = metric
        self.timestamp = datetime.now()
        
    def __repr__(self) -> str:
        return f"[{self.level.value}] {self.timestamp.strftime('%H:%M:%S')} - {self.message}"


class AlertManager:
    """Manages alert generation and history."""
    
    def __init__(self, max_alerts: int = 1000):
        """
        Initialize alert manager.
        
        Args:
            max_alerts: Maximum number of alerts to store
        """
        self.alerts: List[Alert] = []
        self.max_alerts = max_alerts
        self.callbacks: List[Callable] = []  # Callbacks when alerts are triggered
        
        # Default thresholds
        self.price_change_threshold = 2.0  # % change
        self.volatility_threshold = 0.02  # 2% volatility
        self.volatility_critical = 0.05   # 5% critical volatility
        
    def add_callback(self, callback: Callable) -> None:
        """
        Register a callback function to be called when alerts are triggered.
        
        Args:
            callback: Function to call with Alert object
        """
        self.callbacks.append(callback)
        
    def _trigger_alert(self, alert: Alert) -> None:
        """
        Trigger an alert and call registered callbacks.
        
        Args:
            alert: Alert object to trigger
        """
        self.alerts.append(alert)
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop(0)
        
        # Call registered callbacks
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Error in alert callback: {e}")
    
    def check_price_alert(self, current_price: float, previous_price: float) -> Optional[Alert]:
        """
        Check if price movement triggers an alert.
        
        Args:
            current_price: Current price
            previous_price: Previous price
            
        Returns:
            Alert object if threshold crossed, None otherwise
        """
        if previous_price == 0:
            return None
        
        price_change_pct = ((current_price - previous_price) / previous_price) * 100
        
        if abs(price_change_pct) > self.price_change_threshold:
            level = AlertLevel.WARNING if abs(price_change_pct) < 5 else AlertLevel.CRITICAL
            message = f"Price {'increased' if price_change_pct > 0 else 'decreased'} by {abs(price_change_pct):.2f}%"
            
            alert = Alert(
                level=level,
                message=message,
                value=price_change_pct,
                threshold=self.price_change_threshold,
                metric="price_change"
            )
            
            self._trigger_alert(alert)
            return alert
        
        return None
    
    def check_volatility_alert(self, volatility: float) -> Optional[Alert]:
        """
        Check if volatility triggers an alert.
        
        Args:
            volatility: Current volatility measure
            
        Returns:
            Alert object if threshold crossed, None otherwise
        """
        if volatility > self.volatility_critical:
            alert = Alert(
                level=AlertLevel.CRITICAL,
                message=f"CRITICAL: Volatility extremely high at {volatility:.4f}",
                value=volatility,
                threshold=self.volatility_critical,
                metric="volatility"
            )
            self._trigger_alert(alert)
            return alert
            
        elif volatility > self.volatility_threshold:
            alert = Alert(
                level=AlertLevel.WARNING,
                message=f"Volatility elevated at {volatility:.4f}",
                value=volatility,
                threshold=self.volatility_threshold,
                metric="volatility"
            )
            self._trigger_alert(alert)
            return alert
        
        return None
    
    def get_recent_alerts(self, n: int = 10) -> List[Alert]:
        """
        Get the most recent alerts.
        
        Args:
            n: Number of recent alerts to retrieve
            
        Returns:
            List of Alert objects
        """
        return self.alerts[-n:] if len(self.alerts) > 0 else []
    
    def get_all_alerts(self) -> List[Alert]:
        """
        Get all stored alerts.
        
        Returns:
            List of all Alert objects
        """
        return self.alerts.copy()
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()
    
    def set_thresholds(self, price_change: Optional[float] = None,
                       volatility: Optional[float] = None,
                       volatility_critical: Optional[float] = None) -> None:
        """
        Set custom alert thresholds.
        
        Args:
            price_change: Price change threshold percentage
            volatility: Volatility warning threshold
            volatility_critical: Volatility critical threshold
        """
        if price_change is not None:
            self.price_change_threshold = price_change
        if volatility is not None:
            self.volatility_threshold = volatility
        if volatility_critical is not None:
            self.volatility_critical = volatility_critical
