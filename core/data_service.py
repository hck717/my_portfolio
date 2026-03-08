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
            # 試用 fast_info 先
            try:
                price = t.fast_info['lastPrice']
                if price and price > 0:
                    return price
            except:
                pass
            
            # Fallback to history
            data = t.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
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
        """獲取過去 12 個月每股股息 - 使用 ticker.info 更穩定"""
        try:
            t = yf.Ticker(ticker)
            info = t.info
            
            # Method 1: trailingAnnualDividendRate (最可靠)
            if 'trailingAnnualDividendRate' in info and info['trailingAnnualDividendRate']:
                rate = info['trailingAnnualDividendRate']
                if rate > 0:
                    print(f"{ticker} dividend (trailingAnnualDividendRate): {rate}")
                    return rate
            
            # Method 2: dividendRate (forward dividend)
            if 'dividendRate' in info and info['dividendRate']:
                rate = info['dividendRate']
                if rate > 0:
                    print(f"{ticker} dividend (dividendRate): {rate}")
                    return rate
            
            # Method 3: dividendYield * price
            if 'dividendYield' in info and info['dividendYield']:
                div_yield = info['dividendYield']
                if 'currentPrice' in info and info['currentPrice']:
                    estimated_div = div_yield * info['currentPrice']
                    if estimated_div > 0:
                        print(f"{ticker} dividend (yield * price): {estimated_div}")
                        return estimated_div
            
            # Method 4: 計算過去 365 天實際派息
            divs = t.dividends
            if not divs.empty:
                one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=365)
                recent_divs = divs[divs.index > one_year_ago]
                
                if not recent_divs.empty:
                    ttm_div = recent_divs.sum()
                    print(f"{ticker} dividend (TTM actual): {ttm_div}")
                    return ttm_div
                
                # Fallback: 用最近 4 次 annualize
                if len(divs) >= 4:
                    last_4 = divs.tail(4).sum()
                    print(f"{ticker} dividend (last 4): {last_4}")
                    return last_4
            
            print(f"{ticker} dividend: 0.0 (no data found)")
            
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
