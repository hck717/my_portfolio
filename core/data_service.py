"""市場數據服務 (yfinance)"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataService:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
    
    def get_price(self, ticker):
        """獲取目前價格"""
        try:
            t = yf.Ticker(ticker)
            data = t.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
        except:
            pass
        return None
    
    def get_prices(self, tickers):
        """獲取多隻 ticker 價格"""
        prices = {}
        for ticker in tickers:
            price = self.get_price(ticker)
            if price:
                prices[ticker] = price
        return prices
    
    def get_ttm_dividend(self, ticker):
        """獲取過去 12 個月每股股息
        
        改用更穩定的方法：
        1. 先試 ticker.info['dividendRate']
        2. 如果無，利用 dividends history 計算
        """
        try:
            t = yf.Ticker(ticker)
            
            # Method 1: 直接用 dividendRate (annual forward dividend)
            info = t.info
            if 'dividendRate' in info and info['dividendRate']:
                return info['dividendRate']
            
            # Method 2: 計算過去 12 個月實際股息
            divs = t.dividends
            
            if divs.empty:
                return 0.0
            
            one_year_ago = datetime.now() - timedelta(days=365)
            recent_divs = divs[divs.index > one_year_ago]
            
            if not recent_divs.empty:
                return recent_divs.sum()
            
            # Method 3: 如果最近 1 年無數據，用最近 4 次派息
            if len(divs) >= 4:
                return divs.tail(4).sum()
            elif len(divs) > 0:
                # 用最近的 annualize
                avg_div = divs.tail(min(4, len(divs))).mean()
                return avg_div * 4  # 假設年派 4 次
            
        except Exception as e:
            print(f"Error fetching dividend for {ticker}: {e}")
        
        return 0.0
    
    def get_ttm_dividends(self, tickers):
        """獲取多隻 ticker 的 TTM 股息"""
        dividends = {}
        for ticker in tickers:
            div = self.get_ttm_dividend(ticker)
            dividends[ticker] = div
        return dividends
    
    def get_close_n_days_ago(self, ticker, n):
        """獲取 n 個交易日前的收市價"""
        try:
            days_to_fetch = max(120, n * 3)
            t = yf.Ticker(ticker)
            hist = t.history(period=f"{days_to_fetch}d")
            
            if len(hist) <= n:
                return None
            
            return hist['Close'].iloc[-(n+1)]
        except:
            return None
    
    def get_yesterday_close(self, ticker):
        """獲取昨日收市價"""
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if len(hist) >= 2:
                return hist['Close'].iloc[-2]
        except:
            pass
        return None
    
    def get_monthly_high(self, ticker):
        """獲取當月最高價"""
        try:
            t = yf.Ticker(ticker)
            today = datetime.now()
            start_of_month = today.replace(day=1)
            hist = t.history(start=start_of_month)
            
            if not hist.empty:
                return hist['High'].max()
        except:
            pass
        return None
