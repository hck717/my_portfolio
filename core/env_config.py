"""Environment configuration - load from .env file"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

env_path = Path(".env")
if env_path.exists():
    load_dotenv(env_path)

class Config:
    """Application configuration from environment variables"""
    
    # Data refresh settings
    REFRESH_INTERVAL_SECONDS: int = int(os.getenv("REFRESH_INTERVAL_SECONDS", "60"))
    
    # Cache settings
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    
    # Network settings
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY_SECONDS: int = int(os.getenv("RETRY_DELAY_SECONDS", "2"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Notifications
    ENABLE_NOTIFICATIONS: bool = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"
    
    # Performance settings
    HISTORY_DAYS: int = int(os.getenv("HISTORY_DAYS", "365"))
    
    # Risk-free rate for Sharpe ratio
    RISK_FREE_RATE: float = float(os.getenv("RISK_FREE_RATE", "0.04"))
    
    @classmethod
    def reload(cls):
        """Reload configuration from environment"""
        load_dotenv(env_path, override=True)

def get_config() -> Config:
    return Config()
