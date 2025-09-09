#!/usr/bin/env python3
"""
Bitcoin Volume Tracker - Cloud Version with Telegram Commands
Control settings directly from Telegram!
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
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Enhanced Telegram bot with command handling."""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.last_update_id = 0
        self.tracker = None  # Will be set later
        
    def send_message(self, message: str, parse_mode: str = "HTML"):
        """Send message to Telegram."""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Telegram error: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send: {e}")
            return False
    
    def get_updates(self):
        """Get new messages from Telegram."""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 1}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and data.get("result"):
                    for update in data["result"]:
                        self.last_update_id = update["update_id"]
                        if "message" in update and "text" in update["message"]:
                            self.handle_command(update["message"]["text"])
        except Exception as e:
            pass  # Silently ignore to not spam logs
    
    def handle_command(self, text: str):
        """Handle Telegram commands."""
        if not self.tracker:
            return
            
        text = text.strip().lower()
        
        # /status - Show current settings
        if text == "/status" or text == "/start":
            self.send_status()
        
        # /z <value> - Set Z-score threshold
        elif text.startswith("/z "):
            try:
                value = float(text.split()[1])
                if 0.5 <= value <= 20:
                    self.tracker.z_threshold = value
                    self.send_message(f"✅ Z-score threshold set to: {value}")
                    self.save_settings()
                else:
                    self.send_message("❌ Z-score must be between 0.5 and 20")
            except:
                self.send_message("❌ Usage: /z 3.5")
        
        # /vol <value> - Set volume multiplier
        elif text.startswith("/vol "):
            try:
                value = float(text.split()[1])
                if 1 <= value <= 100:
                    self.tracker.volume_threshold = value
                    self.send_message(f"✅ Volume multiplier set to: {value}x")
                    self.save_settings()
                else:
                    self.send_message("❌ Volume must be between 1 and 100")
            except:
                self.send_message("❌ Usage: /vol 2.5")
        
        # /cooldown <seconds> - Set cooldown
        elif text.startswith("/cooldown "):
            try:
                value = int(text.split()[1])
                if 10 <= value <= 3600:
                    self.tracker.alert_cooldown = value
                    self.send_message(f"✅ Cooldown set to: {value} seconds")
                    self.save_settings()
                else:
                    self.send_message("❌ Cooldown must be between 10 and 3600 seconds")
            except:
                self.send_message("❌ Usage: /cooldown 60")
        
        # /whale <value> - Set whale threshold
        elif text.startswith("/whale "):
            try:
                value = float(text.split()[1])
                if value >= 10000:
                    self.tracker.whale_threshold = value
                    self.send_message(f"✅ Whale threshold set to: ${value:,.0f}")
                    self.save_settings()
                else:
                    self.send_message("❌ Whale threshold must be at least $10,000")
            except:
                self.send_message("❌ Usage: /whale 100000")
        
        # /pause - Pause alerts
        elif text == "/pause":
            self.tracker.paused = True
            self.send_message("⏸️ Alerts paused. Use /resume to continue.")
        
        # /resume - Resume alerts
        elif text == "/resume":
            self.tracker.paused = False
            self.send_message("▶️ Alerts resumed!")
        
        # /stats - Show statistics
        elif text == "/stats":
            self.send_stats()
        
        # /help - Show commands
        elif text == "/help":
            self.send_help()
        
        # /test - Send test alert
        elif text == "/test":
            self.send_message(
                "🧪 <b>Test Alert</b>\n\n"
                "If you see this, notifications are working!\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}"
            )
    
    def send_status(self):
        """Send current status."""
        if not self.tracker:
            return
            
        status_msg = f"""
📊 <b>Bitcoin Tracker Status</b>

<b>Settings:</b>
• Z-Score Threshold: {self.tracker.z_threshold}
• Volume Multiplier: {self.tracker.volume_threshold}x
• Cooldown: {self.tracker.alert_cooldown}s
• Whale Threshold: ${self.tracker.whale_threshold:,.0f}
• Status: {'⏸️ Paused' if self.tracker.paused else '▶️ Active'}

<b>Statistics:</b>
• Alerts sent: {self.tracker.alert_count}
• Uptime: {self.get_uptime()}
• Last alert: {self.get_last_alert_time()}

<b>Commands:</b>
/help - Show all commands
/stats - Show statistics
"""
        self.send_message(status_msg)
    
    def send_help(self):
        """Send help message."""
        help_msg = """
📖 <b>Available Commands</b>

<b>View Settings:</b>
/status - Show current settings
/stats - Show statistics

<b>Modify Settings:</b>
/z <value> - Set Z-score (0.5-20)
  Example: /z 3.5

/vol <value> - Set volume multiplier (1-100)
  Example: /vol 2.5

/cooldown <seconds> - Set cooldown (10-3600)
  Example: /cooldown 60

/whale <amount> - Set whale threshold
  Example: /whale 100000

<b>Control:</b>
/pause - Pause alerts
/resume - Resume alerts
/test - Send test notification

<b>Examples:</b>
• Less alerts: /z 5
• More alerts: /z 2
• Only big moves: /vol 5
• Detect smaller whales: /whale 50000
"""
        self.send_message(help_msg)
    
    def send_stats(self):
        """Send statistics."""
        if not self.tracker:
            return
            
        stats_msg = f"""
📈 <b>Tracker Statistics</b>

<b>Performance:</b>
• Total alerts: {self.tracker.alert_count}
• Whale detections: {self.tracker.whale_count}
• Uptime: {self.get_uptime()}
• Start time: {self.tracker.start_time}

<b>Last Values:</b>
• Price: ${self.tracker.last_price:.2f}
• Volume (3s): ${self.tracker.last_volume:.0f}
• Z-Score: {self.tracker.last_zscore:.2f}

<b>Current Settings:</b>
• Z-threshold: {self.tracker.z_threshold}
• Vol multiplier: {self.tracker.volume_threshold}x
• Cooldown: {self.tracker.alert_cooldown}s
"""
        self.send_message(stats_msg)
    
    def get_uptime(self):
        """Calculate uptime."""
        if not self.tracker:
            return "Unknown"
        
        delta = time.time() - self.tracker.start_timestamp
        hours = int(delta // 3600)
        minutes = int((delta % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    def get_last_alert_time(self):
        """Get last alert time."""
        if not self.tracker or self.tracker.last_alert_time == 0:
            return "None"
        
        delta = time.time() - self.tracker.last_alert_time
        if delta < 60:
            return f"{int(delta)}s ago"
        elif delta < 3600:
            return f"{int(delta/60)}m ago"
        else:
            return f"{int(delta/3600)}h ago"
    
    def save_settings(self):
        """Save settings to file (for persistence)."""
        if not self.tracker:
            return
            
        settings = {
            "z_threshold": self.tracker.z_threshold,
            "volume_threshold": self.tracker.volume_threshold,
            "alert_cooldown": self.tracker.alert_cooldown,
            "whale_threshold": self.tracker.whale_threshold
        }
        
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f)
            logger.info("Settings saved")
        except:
            pass
    
    def load_settings(self):
        """Load settings from file."""
        try:
            with open("settings.json", "r") as f:
                return json.load(f)
        except:
            return None

class CloudBinanceTracker:
    """Bitcoin tracker with Telegram control."""
    
    def __init__(self, telegram_bot: TelegramBot):
        self.symbol = "btcusdt"
        self.ws_url = "wss://fstream.binance.com/ws/btcusdt@aggTrade"
        self.ws = None
        self.running = False
        self.paused = False
        
        # Components
        self.bot = telegram_bot
        self.bot.tracker = self  # Link bot to tracker
        
        # Metrics storage
        self.volumes = []
        self.prices = []
        self.timestamps = []
        self.max_buffer = 3600
        
        # Settings (can be modified via Telegram)
        self.z_threshold = 3.0
        self.volume_threshold = 2.0
        self.alert_cooldown = 60
        self.whale_threshold = 100000
        
        # Load saved settings
        saved = self.bot.load_settings()
        if saved:
            self.z_threshold = saved.get("z_threshold", 3.0)
            self.volume_threshold = saved.get("volume_threshold", 2.0)
            self.alert_cooldown = saved.get("alert_cooldown", 60)
            self.whale_threshold = saved.get("whale_threshold", 100000)
        
        # Statistics
        self.alert_count = 0
        self.whale_count = 0
        self.last_alert_time = 0
        self.start_timestamp = time.time()
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Last values for stats
        self.last_price = 0
        self.last_volume = 0
        self.last_zscore = 0
        
        # Start command handler thread
        self.command_thread = threading.Thread(target=self.command_handler, daemon=True)
        self.command_thread.start()
    
    def command_handler(self):
        """Handle Telegram commands in background."""
        while True:
            try:
                self.bot.get_updates()
                time.sleep(2)  # Check every 2 seconds
            except:
                time.sleep(5)
    
    def on_message(self, ws, message):
        """Handle WebSocket message."""
        try:
            data = json.loads(message)
            
            # Extract trade data
            price = float(data['p'])
            quantity = float(data['q'])
            volume = price * quantity
            timestamp = data['T'] / 1000
            
            # Update last values
            self.last_price = price
            
            # Add to buffers
            self.timestamps.append(timestamp)
            self.prices.append(price)
            self.volumes.append(volume)
            
            # Maintain buffer size
            if len(self.timestamps) > self.max_buffer:
                self.timestamps.pop(0)
                self.prices.pop(0)
                self.volumes.pop(0)
            
            # Calculate metrics
            if len(self.volumes) >= 60:
                metrics = self.calculate_metrics()
                if metrics and not self.paused:
                    self.check_alerts(metrics)
            
            # Log every 30 seconds
            if int(timestamp) % 30 == 0:
                logger.info(f"📊 Price: ${price:.2f} | Vol: ${volume:.0f}")
                
        except Exception as e:
            logger.error(f"Error processing: {e}")
    
    def calculate_metrics(self):
        """Calculate metrics."""
        if len(self.volumes) < 60:
            return None
            
        # Last 3 seconds volume
        recent_vol = sum(self.volumes[-3:]) if len(self.volumes) >= 3 else 0
        self.last_volume = recent_vol
        
        # 60s average
        avg_vol = sum(self.volumes[-60:]) / 60
        
        # Z-score
        import statistics
        mean = statistics.mean(self.volumes[-60:])
        stdev = statistics.stdev(self.volumes[-60:])
        z_score = (recent_vol - mean) / stdev if stdev > 0 else 0
        self.last_zscore = z_score
        
        # Whale detection
        is_whale = recent_vol > self.whale_threshold
        
        return {
            'vol_3s': recent_vol,
            'avg_60s': avg_vol,
            'z_score': z_score,
            'is_whale': is_whale,
            'price': self.prices[-1] if self.prices else 0
        }
    
    def check_alerts(self, metrics):
        """Check alert conditions."""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
            
        z_score = metrics['z_score']
        vol_ratio = metrics['vol_3s'] / metrics['avg_60s'] if metrics['avg_60s'] > 0 else 0
        
        alert_triggered = False
        alert_message = ""
        
        # High volume alert
        if z_score >= self.z_threshold and vol_ratio >= self.volume_threshold:
            alert_triggered = True
            self.alert_count += 1
            alert_message = f"""
🚨 <b>HIGH VOLUME ALERT #{self.alert_count}</b>

📊 <b>Bitcoin</b>: ${metrics['price']:.2f}
📈 <b>Volume (3s)</b>: ${metrics['vol_3s']:,.0f}
📉 <b>Avg (60s)</b>: ${metrics['avg_60s']:,.0f}
⚡ <b>Ratio</b>: {vol_ratio:.1f}x
📐 <b>Z-Score</b>: {z_score:.2f}

⚙️ Settings: Z≥{self.z_threshold} Vol≥{self.volume_threshold}x
"""
        
        # Whale alert
        elif metrics['is_whale'] and z_score >= 2.0:
            alert_triggered = True
            self.whale_count += 1
            alert_message = f"""
🐋 <b>WHALE DETECTED #{self.whale_count}</b>

💰 <b>Large Volume</b>: ${metrics['vol_3s']:,.0f}
📊 <b>Price</b>: ${metrics['price']:.2f}
📐 <b>Z-Score</b>: {z_score:.2f}
🎯 <b>Threshold</b>: ${self.whale_threshold:,.0f}
"""
        
        if alert_triggered:
            self.bot.send_message(alert_message)
            self.last_alert_time = current_time
            logger.info(f"Alert sent! #{self.alert_count}")
    
    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        logger.info("WebSocket closed")
        self.running = False
    
    def on_open(self, ws):
        logger.info("✅ Connected to Binance")
        self.running = True
        
        # Send startup message
        self.bot.send_message(f"""
🟢 <b>Bitcoin Tracker Started</b>

<b>Monitoring:</b> BTCUSDT
<b>Settings:</b>
• Z-Score: ≥{self.z_threshold}
• Volume: ≥{self.volume_threshold}x average
• Cooldown: {self.alert_cooldown}s
• Whale: >${self.whale_threshold:,.0f}

<b>Commands:</b>
/status - View settings
/help - Show all commands

<i>You can modify settings anytime!</i>
""")
    
    def start(self):
        """Start the tracker."""
        logger.info("Starting tracker with Telegram control...")
        
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
                logger.info("Stopping...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(10)

def main():
    """Main entry point."""
    
    # Get credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        sys.exit(1)
    
    # Create bot and tracker
    bot = TelegramBot(bot_token, chat_id)
    tracker = CloudBinanceTracker(bot)
    
    try:
        tracker.start()
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
