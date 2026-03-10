"""市場數據服務 (yfinance) - with retry, cache, and offline support"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import warnings
import requests
from core.logger import logger
from core.env_config import get_config

warnings.filterwarnings('ignore')

config = get_config()

class CacheEntry:
    """Cache entry with TTL"""
    def __init__(self, value, ttl: int):
        self.value = value
        self.timestamp = time.time()
        self.ttl = ttl
    
    def is_valid(self) -> bool:
        return time.time() - self.timestamp < self.ttl

class DataService:
    """Market data service with caching, retry, and offline support"""
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_ttl = config.CACHE_TTL_SECONDS
        self.max_retries = config.MAX_RETRIES
        self.retry_delay = config.RETRY_DELAY_SECONDS
        self._offline_mode = False
        self._last_successful_fetch: Optional[datetime] = None
    
    def is_online(self) -> bool:
        """Check if network is available"""
        if self._offline_mode:
            return False
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except:
            self._offline_mode = True
            logger.warning("Network unavailable, switching to offline mode")
            return False
    
    def get_from_cache(self, key: str) -> Optional[any]:
        """Get value from cache if valid"""
        if key in self.cache:
            entry = self.cache[key]
            if entry.is_valid():
                return entry.value
            else:
                del self.cache[key]
        return None
    
    def set_cache(self, key: str, value: any):
        """Set cache with TTL"""
        self.cache[key] = CacheEntry(value, self.cache_ttl)
    
    def clear_cache(self):
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def _fetch_with_retry(self, fetch_func, *args, **kwargs):
        """Execute fetch function with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return fetch_func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                continue
        
        logger.error(f"All {self.max_retries} attempts failed: {last_error}")
        return None
    
    def get_price(self, ticker: str) -> Optional[float]:
        """Get current price with caching and retry"""
        cache_key = f"price_{ticker}"
        
        cached = self.get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        if not self.is_online():
            logger.warning(f"Offline mode: cannot fetch price for {ticker}")
            return None
        
        def fetch():
            t = yf.Ticker(ticker)
            try:
                price = t.fast_info['lastPrice']
                if price and price > 0:
                    return float(price)
            except:
                pass
            
            data = t.history(period="1d")
            if data is not None and not data.empty:
                return float(data['Close'].iloc[-1])
            return None
        
        price = self._fetch_with_retry(fetch)
        
        if price is not None:
            self.set_cache(cache_key, price)
            self._last_successful_fetch = datetime.now()
            logger.info(f"Fetched price for {ticker}: ${price:.2f}")
        
        return price
    
    def get_prices(self, tickers: List[str]) -> Dict[str, float]:
        """Get multiple ticker prices"""
        prices = {}
        for ticker in tickers:
            price = self.get_price(ticker)
            if price:
                prices[ticker] = price
        return prices
    
    def get_ttm_dividend(self, ticker: str, max_retries: int = None) -> float:
        """Get TTM dividend with retry"""
        if max_retries is None:
            max_retries = self.max_retries
        
        cache_key = f"dividend_{ticker}"
        
        cached = self.get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        if not self.is_online():
            logger.warning(f"Offline mode: cannot fetch dividend for {ticker}")
            return 0.0
        
        for attempt in range(max_retries):
            try:
                t = yf.Ticker(ticker)
                
                try:
                    info = t.info
                except Exception as info_err:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    logger.warning(f"Could not fetch info for {ticker}: {info_err}")
                    info = {}
                
                if 'trailingAnnualDividendRate' in info and info['trailingAnnualDividendRate']:
                    rate = info['trailingAnnualDividendRate']
                    if rate > 0:
                        logger.info(f"{ticker} dividend (trailing): {rate}")
                        self.set_cache(cache_key, float(rate))
                        return float(rate)
                
                if 'dividendRate' in info and info['dividendRate']:
                    rate = info['dividendRate']
                    if rate > 0:
                        logger.info(f"{ticker} dividend (rate): {rate}")
                        self.set_cache(cache_key, float(rate))
                        return float(rate)
                
                if 'dividendYield' in info and info['dividendYield']:
                    div_yield = info['dividendYield']
                    if 'currentPrice' in info and info['currentPrice']:
                        estimated_div = div_yield * info['currentPrice']
                        if estimated_div > 0:
                            logger.info(f"{ticker} dividend (yield*price): {estimated_div}")
                            self.set_cache(cache_key, float(estimated_div))
                            return float(estimated_div)
                
                try:
                    divs = t.dividends
                    if divs is not None and len(divs) > 0:
                        divs_index = pd.DatetimeIndex(divs.index).tz_localize(None)
                        one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=365)
                        
                        recent_divs = divs[divs_index > one_year_ago]
                        
                        if len(recent_divs) > 0:
                            ttm_div = recent_divs.sum()
                            logger.info(f"{ticker} dividend (TTM): {ttm_div}")
                            self.set_cache(cache_key, float(ttm_div))
                            return float(ttm_div)
                        
                        if len(divs) >= 4:
                            last_4 = divs.tail(4).sum()
                            logger.info(f"{ticker} dividend (last 4): {last_4}")
                            self.set_cache(cache_key, float(last_4))
                            return float(last_4)
                except Exception as div_err:
                    logger.warning(f"Could not fetch dividends for {ticker}: {div_err}")
                
                logger.info(f"{ticker} dividend: 0.0 (no data)")
                return 0.0
                
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                logger.error(f"Error fetching dividend for {ticker}: {e}")
        
        return 0.0
    
    def get_ttm_dividends(self, tickers: List[str]) -> Dict[str, float]:
        """Get multiple ticker dividends"""
        dividends = {}
        for ticker in tickers:
            dividends[ticker] = self.get_ttm_dividend(ticker)
        return dividends
    
    def get_close_n_days_ago(self, ticker: str, n: int) -> Optional[float]:
        """Get close price n days ago"""
        cache_key = f"close_{ticker}_{n}"
        
        cached = self.get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        if not self.is_online():
            return None
        
        def fetch():
            days_to_fetch = max(120, n * 3)
            t = yf.Ticker(ticker)
            hist = t.history(period=f"{days_to_fetch}d")
            
            if hist is None or len(hist) <= n:
                return None
            
            return float(hist['Close'].iloc[-(n+1)])
        
        price = self._fetch_with_retry(fetch)
        
        if price is not None:
            self.set_cache(cache_key, price)
        
        return price
    
    def get_yesterday_close(self, ticker: str) -> Optional[float]:
        """Get yesterday's close price"""
        cache_key = f"yesterday_{ticker}"
        
        cached = self.get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        if not self.is_online():
            return None
        
        def fetch():
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if hist is not None and len(hist) >= 2:
                return float(hist['Close'].iloc[-2])
            return None
        
        price = self._fetch_with_retry(fetch)
        
        if price is not None:
            self.set_cache(cache_key, price)
        
        return price
    
    def get_monthly_high(self, ticker: str) -> Optional[float]:
        """Get monthly high price"""
        cache_key = f"monthly_high_{ticker}"
        
        cached = self.get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        if not self.is_online():
            return None
        
        def fetch():
            t = yf.Ticker(ticker)
            today = datetime.now()
            start_of_month = today.replace(day=1)
            hist = t.history(start=start_of_month)
            
            if hist is not None and not hist.empty:
                return float(hist['High'].max())
            return None
        
        price = self._fetch_with_retry(fetch)
        
        if price is not None:
            self.set_cache(cache_key, price)
        
        return price
    
    def get_historical_prices(self, ticker: str, start_date: str, end_date: str = None) -> Optional[pd.DataFrame]:
        """Get historical price data"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if not self.is_online():
            logger.warning(f"Offline mode: cannot fetch historical data for {ticker}")
            return None
        
        def fetch():
            t = yf.Ticker(ticker)
            hist = t.history(start=start_date, end=end_date)
            return hist
        
        return self._fetch_with_retry(fetch)
