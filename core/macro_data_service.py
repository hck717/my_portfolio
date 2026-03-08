"""Macro economic indicators data service"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests

class MacroDataService:
    """自動抓取宏觀經濟指標"""
    
    def __init__(self):
        self.cache = {}
    
    def get_yield_curve_spread(self):
        """獲取 10Y-3M yield spread"""
        try:
            # 用 yfinance 抓 10Y 同 3M Treasury yield
            tnx = yf.Ticker("^TNX")  # 10-Year Treasury
            irx = yf.Ticker("^IRX")  # 3-Month Treasury
            
            tnx_data = tnx.history(period="5d")
            irx_data = irx.history(period="5d")
            
            if not tnx_data.empty and not irx_data.empty:
                ten_year = tnx_data['Close'].iloc[-1]
                three_month = irx_data['Close'].iloc[-1]
                spread = ten_year - three_month
                
                # 返回 1 如果倒掛（spread < 0），否則 0
                return 1 if spread < 0 else 0, spread
        except:
            pass
        return 0, None
    
    def get_lei_signal(self):
        """獲取 LEI recession signal"""
        # LEI 數據需要 FRED API 或者手動輸入
        # 暫時返回 cached value，用戶可手動更新
        return self.cache.get('lei_signal', 0)
    
    def get_sahm_rule_signal(self):
        """獲取 Sahm Rule signal"""
        # Sahm Rule 數據需要 FRED API 或者手動輸入
        # 暫時返回 cached value，用戶可手動更新
        return self.cache.get('sahm_rule_signal', 0)
    
    def update_cache(self, indicator, value):
        """更新 cache"""
        self.cache[indicator] = value
    
    def get_all_signals(self):
        """獲取所有宏觀指標"""
        yield_inverted, spread = self.get_yield_curve_spread()
        lei = self.get_lei_signal()
        sahm = self.get_sahm_rule_signal()
        
        return {
            'yield_curve_inverted': yield_inverted,
            'yield_spread': spread,
            'lei_signal': lei,
            'sahm_rule_signal': sahm
        }
