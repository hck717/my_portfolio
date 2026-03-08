"""交易規則引擎"""
from core.config import (
    RULE1_BUY1_THRESHOLD,
    RULE1_BUY2_THRESHOLD,
    RULE1_BUY3_THRESHOLD,
    TACTICAL_DROP_THRESHOLD,
    TARGET_WEIGHTS
)
from datetime import datetime

class RulesEngine:
    def __init__(self, data_service):
        self.data_service = data_service
    
    def check_rule1_triggers(self, rsp_price, rsp_yesterday, rsp_monthly_high):
        """檢查 Rule 1 買入觸發"""
        triggers = {
            "buy1": False,
            "buy2": False,
            "buy3": False,
            "fallback": False
        }
        
        if rsp_yesterday and rsp_price:
            daily_change = (rsp_price / rsp_yesterday) - 1
            if daily_change <= RULE1_BUY1_THRESHOLD:
                triggers["buy1"] = True
        
        if rsp_monthly_high and rsp_price:
            monthly_dd = (rsp_price / rsp_monthly_high) - 1
            if monthly_dd <= RULE1_BUY2_THRESHOLD:
                triggers["buy2"] = True
            if monthly_dd <= RULE1_BUY3_THRESHOLD:
                triggers["buy3"] = True
        
        today = datetime.now()
        if today.weekday() == 4 and 15 <= today.day <= 21:
            triggers["fallback"] = True
        
        return triggers
    
    def calculate_rule1_investments(self, monthly_minimum, prices):
        """計算 Rule 1 每次買入的分配金額"""
        investments = {}
        
        for ticker, weight in TARGET_WEIGHTS.items():
            if ticker in prices:
                amount = monthly_minimum * weight
                shares = amount / prices[ticker]
                
                investments[ticker] = {
                    "amount_usd": amount,
                    "shares": shares,
                    "price": prices[ticker]
                }
        
        return investments
    
    def check_rule2_trigger(self, iwy_current, iwy_40d_ago, spmo_current, spmo_40d_ago):
        """檢查 Rule 2 tactical 觸發"""
        if not all([iwy_current, iwy_40d_ago, spmo_current, spmo_40d_ago]):
            return False, None, None
        
        iwy_40d_return = (iwy_current / iwy_40d_ago) - 1
        spmo_40d_return = (spmo_current / spmo_40d_ago) - 1
        
        triggered = (iwy_40d_return <= TACTICAL_DROP_THRESHOLD and 
                    spmo_40d_return <= TACTICAL_DROP_THRESHOLD)
        
        return triggered, iwy_40d_return, spmo_40d_return
    
    def calculate_rule2_investments(self, bnd_holdings_value, prices):
        """計算 Rule 2 tactical 買入金額
        
        Args:
            bnd_holdings_value: 目前 BND 持倉市值 (USD)
            prices: ETF 價格
        """
        sell_bnd_amount = bnd_holdings_value * 0.5  # 賣 50% BND
        
        iwy_buy = sell_bnd_amount * 0.5
        spmo_buy = sell_bnd_amount * 0.5
        
        result = {
            "sell_bnd_amount": sell_bnd_amount,
            "iwy_buy_amount": iwy_buy,
            "spmo_buy_amount": spmo_buy
        }
        
        if "IWY" in prices:
            result["iwy_shares"] = iwy_buy / prices["IWY"]
        
        if "SPMO" in prices:
            result["spmo_shares"] = spmo_buy / prices["SPMO"]
        
        if "BND" in prices:
            result["sell_bnd_shares"] = sell_bnd_amount / prices["BND"]
        
        return result
    
    def check_macro_regime(self, lei_signal, yield_curve_inverted, sahm_rule_signal):
        """檢查宏觀經濟週期
        
        Returns:
            Expansion / Peak / Contraction / Trough
        """
        signals = [lei_signal, yield_curve_inverted, sahm_rule_signal]
        count = sum(signals)
        
        if count == 0:
            return "Expansion"
        elif count == 1:
            return "Peak"
        elif count >= 2:
            return "Contraction"
        else:
            # Trough 需要手動判斷
            return "Expansion"
    
    def check_cash_gate(self, current_cash_usd, cash_floor_usd):
        """檢查現金是否高於底線"""
        return current_cash_usd >= cash_floor_usd
    
    def evaluate_rule2_final(self, price_trigger, macro_regime, cash_above_floor):
        """最終 Rule 2 執行決定"""
        if not price_trigger:
            return "No Trigger"
        
        if macro_regime != "Expansion":
            return "Blocked by Macro"
        
        if not cash_above_floor:
            return "Blocked by Cash"
        
        return "Execute"
