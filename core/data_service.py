"""Market data service using yfinance"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataService:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
    
    def get_price(self, ticker):
        """Get current price"""
        try:
            t = yf.Ticker(ticker)
            data = t.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
        except:
            pass
        return None
    
    def get_prices(self, tickers):
        """Get prices for multiple tickers"""
        prices = {}
        for ticker in tickers:
            price = self.get_price(ticker)
            if price:
                prices[ticker] = price
        return prices
    
    def get_ttm_dividend(self, ticker):
        """Get trailing 12-month dividend per share"""
        try:
            t = yf.Ticker(ticker)
            divs = t.dividends
            
            if divs.empty:
                return 0.0
            
            one_year_ago = datetime.now() - timedelta(days=365)
            recent_divs = divs[divs.index > one_year_ago]
            
            return recent_divs.sum()
        except:
            return 0.0
    
    def get_ttm_dividends(self, tickers):
        """Get TTM dividends for multiple tickers"""
        dividends = {}
        for ticker in tickers:
            div = self.get_ttm_dividend(ticker)
            dividends[ticker] = div
        return dividends
    
    def get_close_n_days_ago(self, ticker, n):
        """Get close price n trading days ago"""
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
        """Get yesterday's close"""
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if len(hist) >= 2:
                return hist['Close'].iloc[-2]
        except:
            pass
        return None
    
    def get_monthly_high(self, ticker):
        """Get current month's high"""
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
