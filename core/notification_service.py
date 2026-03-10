"""Notification service for macOS"""
import os
import subprocess
from typing import Optional
from core.logger import logger
from core.env_config import get_config

config = get_config()

def send_notification(title: str, message: str, sound: bool = True) -> bool:
    """Send macOS notification using osascript"""
    if not config.ENABLE_NOTIFICATIONS:
        logger.info(f"Notifications disabled, skipping: {title}")
        return False
    
    try:
        script = f'display notification "{message}" with title "{title}"'
        if sound:
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
        
        subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
        logger.info(f"Notification sent: {title} - {message}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False

def send_rule1_alert(rule_type: str, triggers: dict) -> bool:
    """Send Rule 1 trigger notification"""
    if not any(triggers.values()):
        return False
    
    active_triggers = [k for k, v in triggers.items() if v]
    message = f"Triggers: {', '.join(active_triggers)}"
    return send_notification("Rule 1 DCA Triggered", message)

def send_rule2_alert(triggered: bool, reason: str = "") -> bool:
    """Send Rule 2 trigger notification"""
    if triggered:
        return send_notification("Rule 2 Tactical Triggered", "Market conditions met for tactical overlay")
    elif reason:
        return send_notification("Rule 2 Blocked", reason)
    return False
