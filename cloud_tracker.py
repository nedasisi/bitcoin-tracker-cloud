#!/usr/bin/env python3
"""
Bitcoin Volume Tracker - Cloud Version with iPhone Notifications
Optimized for running 24/7 on free cloud services
"""

import os
import sys
import time
import json
import asyncio
import logging
import requests
from datetime import datetime
from typing import Optional
import websocket
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Send notifications to iPhone via Telegram."""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_alert(self, message: str, parse_mode: str = "HTML"):
        """Send alert to Telegram."""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Telegram notification sent")
                return True
            else:
                logger.error(f"❌ Telegram error: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram: {e}")
            return False

class SimpleMetricsCalculator:
    """Lightweight metrics calculator for cloud."""
    
    def __init__(self):
        self.volumes = []
        self.prices = []
        self.timestamps = []
        self.max_buffer = 3600  # Keep last hour
        
    def add_trade(self, timestamp: float, price: float, volume: float):
        """Add trade and maintain buffer."""
        self.timestamps.append(timestamp)
        self.prices.append(price)
        self.volumes.append(volume)
        
        # Keep only last hour
        if len(self.timestamps) > self.max_buffer:
            self.timestamps.pop(0)
            self.prices.pop(0)
            self.volumes.pop(0)
    
    def calculate_metrics(self):
        """Calculate key metrics."""
        if len(self.volumes) < 60:
            return None
            
        # Last 3 seconds volume
        recent_vol = sum(self.volumes[-3:]) if len(self.volumes) >= 3 else 0
        
        # 60s average
        avg_vol = sum(self.volumes[-60:]) / 60
        
        # Z-score
        if len(self.volumes) >= 60:
            import statistics
            mean = statistics.mean(self.volumes[-60:])
            stdev = statistics.stdev(self.volumes[-60:])
            z_score = (recent_vol - mean) / stdev if stdev > 0 else 0
        else:
            z_score = 0
            
        # Whale detection
        is_whale = recent_vol > 100000  # $100k threshold
        
        return {
            'vol_3s': recent_vol,
            'avg_60s': avg_vol,
            'z_score': z_score,
            'is_whale': is_whale,
            'price': self.prices[-1] if self.prices else 0
        }

class CloudBinanceTracker:
    """Lightweight Binance tracker for cloud deployment."""
    
    def __init__(self, telegram_bot_token: str, telegram_chat_id: str):
        self.symbol = "btcusdt"
        self.ws_url = "wss://fstream.binance.com/ws/btcusdt@aggTrade"
        self.ws = None
        self.running = False
        
        # Components
        self.calculator = SimpleMetricsCalculator()
        self.notifier = TelegramNotifier(telegram_bot_token, telegram_chat_id)
        
        # Alert settings
        self.z_threshold = 3.0
        self.volume_threshold = 2.0  # 2x average
        self.last_alert_time = 0
        self.alert_cooldown = 60  # 60 seconds between alerts
        
    def on_message(self, ws, message):
        """Handle WebSocket message."""
        try:
            data = json.loads(message)
            
            # Extract trade data
            price = float(data['p'])
            quantity = float(data['q'])
            volume = price * quantity
            timestamp = data['T'] / 1000  # Convert to seconds
            
            # Add to calculator
            self.calculator.add_trade(timestamp, price, volume)
            
            # Calculate metrics
            metrics = self.calculator.calculate_metrics()
            
            if metrics:
                # Check for alerts
                self.check_alerts(metrics)
                
                # Log every 30 seconds
                if int(timestamp) % 30 == 0:
                    logger.info(f"📊 Price: ${price:.2f} | Vol(3s): ${metrics['vol_3s']:.0f} | Z: {metrics['z_score']:.2f}")
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def check_alerts(self, metrics):
        """Check if alert conditions are met."""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
            
        # Check conditions
        z_score = metrics['z_score']
        vol_ratio = metrics['vol_3s'] / metrics['avg_60s'] if metrics['avg_60s'] > 0 else 0
        
        alert_triggered = False
        alert_message = ""
        
        # High volume alert
        if z_score >= self.z_threshold and vol_ratio >= self.volume_threshold:
            alert_triggered = True
            alert_message = f"""
🚨 <b>HIGH VOLUME ALERT</b> 🚨

📊 <b>Bitcoin</b>: ${metrics['price']:.2f}
📈 <b>Volume (3s)</b>: ${metrics['vol_3s']:,.0f}
📉 <b>Avg (60s)</b>: ${metrics['avg_60s']:,.0f}
⚡ <b>Ratio</b>: {vol_ratio:.1f}x
📐 <b>Z-Score</b>: {z_score:.2f}

🕐 Time: {datetime.now().strftime('%H:%M:%S')}
"""
        
        # Whale alert
        elif metrics['is_whale'] and z_score >= 2.0:
            alert_triggered = True
            alert_message = f"""
🐋 <b>WHALE DETECTED</b> 🐋

💰 <b>Large Volume</b>: ${metrics['vol_3s']:,.0f}
📊 <b>Price</b>: ${metrics['price']:.2f}
📐 <b>Z-Score</b>: {z_score:.2f}

🕐 Time: {datetime.now().strftime('%H:%M:%S')}
"""
        
        if alert_triggered:
            self.notifier.send_alert(alert_message)
            self.last_alert_time = current_time
            logger.info(f"🔔 Alert sent! Z={z_score:.2f}, Ratio={vol_ratio:.1f}x")
    
    def on_error(self, ws, error):
        """Handle WebSocket error."""
        logger.error(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close."""
        logger.info("WebSocket closed")
        self.running = False
    
    def on_open(self, ws):
        """Handle WebSocket open."""
        logger.info("✅ Connected to Binance WebSocket")
        self.running = True
        
        # Send initial notification
        self.notifier.send_alert(
            "🟢 <b>Bitcoin Tracker Started</b>\n\n"
            f"Monitoring: BTCUSDT\n"
            f"Z-Score Threshold: {self.z_threshold}\n"
            f"Volume Multiplier: {self.volume_threshold}x\n\n"
            "You will receive alerts when high volume is detected!"
        )
    
    def start(self):
        """Start the tracker."""
        logger.info("Starting Cloud Bitcoin Tracker...")
        
        while True:
            try:
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                
                self.ws.run_forever()
                
                if not self.running:
                    logger.info("Reconnecting in 5 seconds...")
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                logger.info("Stopping tracker...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(10)

def main():
    """Main entry point."""
    
    # Get credentials from environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("\n" + "="*60)
        print("⚠️  CONFIGURATION REQUIRED")
        print("="*60)
        print("\nPlease set environment variables:")
        print("  TELEGRAM_BOT_TOKEN = your_bot_token")
        print("  TELEGRAM_CHAT_ID = your_chat_id")
        print("\nHow to get them:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get your chat ID with @userinfobot")
        print("="*60)
        
        # For testing, allow manual input
        bot_token = input("\nEnter Bot Token (or press Enter to exit): ").strip()
        if not bot_token:
            sys.exit(1)
        chat_id = input("Enter Chat ID: ").strip()
    
    # Create and start tracker
    tracker = CloudBinanceTracker(bot_token, chat_id)
    
    try:
        tracker.start()
    except KeyboardInterrupt:
        logger.info("Tracker stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
