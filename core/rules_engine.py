"""Trading rules engine"""
from core.config import (
    RULE1_BUY1_THRESHOLD,
    RULE1_BUY2_THRESHOLD,
    RULE1_BUY3_THRESHOLD,
    TACTICAL_DROP_THRESHOLD
)
from datetime import datetime

class RulesEngine:
    def __init__(self, data_service):
        self.data_service = data_service
    
    def check_rule1_triggers(self, rsp_price, rsp_yesterday, rsp_monthly_high):
        """Check Rule 1 buy triggers"""
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
    
    def check_rule2_trigger(self, iwy_current, iwy_40d_ago, spmo_current, spmo_40d_ago):
        """Check Rule 2 tactical trigger"""
        if not all([iwy_current, iwy_40d_ago, spmo_current, spmo_40d_ago]):
            return False, None, None
        
        iwy_40d_return = (iwy_current / iwy_40d_ago) - 1
        spmo_40d_return = (spmo_current / spmo_40d_ago) - 1
        
        triggered = (iwy_40d_return <= TACTICAL_DROP_THRESHOLD and 
                    spmo_40d_return <= TACTICAL_DROP_THRESHOLD)
        
        return triggered, iwy_40d_return, spmo_40d_return
    
    def check_macro_regime(self, lei_signal, yield_curve_inverted, sahm_rule_signal):
        """Check macro regime"""
        signals = [lei_signal, yield_curve_inverted, sahm_rule_signal]
        count = sum(signals)
        
        if count == 0:
            return "Normal"
        elif count == 1:
            return "Caution"
        else:
            return "Recession"
    
    def check_cash_gate(self, current_cash_usd, cash_floor_usd):
        """Check if cash is above floor"""
        return current_cash_usd >= cash_floor_usd
    
    def evaluate_rule2_final(self, price_trigger, macro_regime, cash_above_floor):
        """Final Rule 2 execution decision"""
        if not price_trigger:
            return "No Trigger"
        
        if macro_regime != "Normal":
            return "Blocked by Macro"
        
        if not cash_above_floor:
            return "Blocked by Cash"
        
        return "Execute"
