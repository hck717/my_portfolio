"""交易規則引擎"""
from core.config import (
    RULE1_BUY1_THRESHOLD,
    RULE1_BUY2_THRESHOLD,
    RULE1_BUY3_THRESHOLD,
    TACTICAL_DROP_THRESHOLD,
    TARGET_WEIGHTS
)
from datetime import datetime

class MacroIndicator:
    """Macro economic indicator"""
    def __init__(self, name, value, threshold, is_active, description):
        self.name = name
        self.value = value
        self.threshold = threshold
        self.is_active = is_active
        self.description = description

class RulesEngine:
    def __init__(self, data_service):
        self.data_service = data_service
        self.macro_indicators = []
    
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
        """計算 Rule 2 tactical 買入金額"""
        sell_bnd_amount = bnd_holdings_value * 0.5
        
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
    
    def check_ai_risk(self, settings, data_service=None):
        """Check AI Risk Flag
        
        AI Risk Conditions:
        1. QQQ (Nasdaq-100 / Magnificent 7) drawdown >= 15% for 2+ months
        2. OR VIX > 25 for 2+ weeks
        
        This is an optional additional risk gate for Tactical Overlay.
        """
        ai_risk = {
            "enabled": settings.get("ai_risk_enabled", False),
            "qqq_drawdown": None,
            "qqq_drawdown_pct": 0,
            "vix_level": None,
            "vix_high": False,
            "is_active": False,
            "reason": ""
        }
        
        if not ai_risk["enabled"]:
            ai_risk["reason"] = "AI Risk Flag disabled"
            return ai_risk
        
        # Get QQQ drawdown data
        qqq_monthly_high = settings.get("qqq_monthly_high", None)
        qqq_current = settings.get("qqq_current", None)
        
        if qqq_current and qqq_monthly_high:
            drawdown = (qqq_current / qqq_monthly_high) - 1
            ai_risk["qqq_drawdown"] = qqq_current
            ai_risk["qqq_drawdown_pct"] = drawdown * 100
            
            # Check if drawdown >= 15% for 2 months
            # We track this via settings (user inputs months above threshold)
            qqq_months_above_threshold = settings.get("qqq_months_above_15pct", 0)
            
            if drawdown <= -0.15 and qqq_months_above_threshold >= 2:
                ai_risk["is_active"] = True
                ai_risk["reason"] = f"QQQ drawdown {drawdown*100:.1f}% for {qqq_months_above_threshold}+ months"
        
        # Get VIX level
        vix_current = settings.get("vix_current", None)
        vix_weeks_above = settings.get("vix_weeks_above_25", 0)
        
        if vix_current:
            ai_risk["vix_level"] = vix_current
            ai_risk["vix_high"] = vix_current > 25
            
            # Check if VIX > 25 for 2+ weeks
            if vix_current > 25 and vix_weeks_above >= 2:
                ai_risk["is_active"] = True
                ai_risk["reason"] = f"VIX {vix_current:.1f} elevated for {vix_weeks_above}+ weeks"
        
        return ai_risk
    
    def check_tactical_exit_signal(self, rsp_price, rsp_40d_ago, iwy_price, iwy_40d_ago, spmo_price, spmo_40d_ago):
        """Check for early tactical exit signal
        
        Exit Signal:
        If RSP outperforms IWY/SPMO by > 10% over 40 days
        → Consider partial exit (30-50% of tactical position)
        
        Returns:
        {
            "should_exit": bool,
            "rsp_return": float,
            "iwy_return": float,
            "spmo_return": float,
            "outperformance": float,
            "exit_percentage": int
        }
        """
        if not all([rsp_price, rsp_40d_ago, iwy_price, iwy_40d_ago, spmo_price, spmo_40d_ago]):
            return {"should_exit": False, "reason": "Insufficient data"}
        
        rsp_return = (rsp_price / rsp_40d_ago) - 1
        iwy_return = (iwy_price / iwy_40d_ago) - 1
        spmo_return = (spmo_price / spmo_40d_ago) - 1
        
        # Average return of IWY/SPMO
        tactical_return = (iwy_return + spmo_return) / 2
        
        # RSP outperformance
        outperformance = rsp_return - tactical_return
        
        result = {
            "should_exit": False,
            "rsp_return": rsp_return,
            "iwy_return": iwy_return,
            "spmo_return": spmo_return,
            "tactical_return": tactical_return,
            "outperformance": outperformance,
            "exit_percentage": 0,
            "reason": ""
        }
        
        # If RSP outperforms by > 10%, suggest partial exit
        if outperformance > 0.10:
            result["should_exit"] = True
            # Exit 30-50% based on outperformance magnitude
            if outperformance > 0.20:
                result["exit_percentage"] = 50
            else:
                result["exit_percentage"] = 30
            result["reason"] = f"RSP outperforms tactical by {outperformance*100:.1f}%"
        
        return result
    
    def evaluate_macro_indicators(self, settings, yield_spread):
        """評估宏觀經濟指標
        
        Indicators:
        1. LEI (Conference Board Leading Economic Index) - YoY decline expanding
        2. 10Y-3M Yield Spread - < 0 (inverted)
        3. Sahm Rule - >= 0.50
        4. CCI Expectations Index - < 80
        5. Initial Jobless Claims (4-week MA) - > 400,000
        """
        indicators = []
        
        # 1. LEI Recession Signal
        lei_signal = settings.get("lei_signal", 0)
        lei_active = lei_signal == 1
        indicators.append(MacroIndicator(
            "LEI Recession Signal",
            "Active" if lei_signal else "Normal",
            "YoY decline expanding",
            lei_active,
            "Conference Board LEI recession signal"
        ))
        
        # 2. 10Y-3M Yield Spread
        yield_inverted = settings.get("yield_curve_inverted", 0)
        yield_active = yield_inverted == 1
        spread_value = yield_spread if yield_spread is not None else 0
        indicators.append(MacroIndicator(
            "10Y-3M Yield Spread",
            f"{spread_value:.2f}%" if spread_value else "N/A",
            "< 0 (inverted)",
            yield_active,
            "Yield curve inverted when < 0"
        ))
        
        # 3. Sahm Rule
        sahm_signal = settings.get("sahm_rule_signal", 0)
        sahm_active = sahm_signal >= 0.50
        indicators.append(MacroIndicator(
            "Sahm Rule",
            f"{sahm_signal:.2f}" if sahm_signal else "0",
            ">= 0.50",
            sahm_active,
            "Sahm recession rule"
        ))
        
        # 4. CCI Expectations Index
        cci_signal = settings.get("cci_signal", 0)
        cci_active = 0 < cci_signal < 80
        indicators.append(MacroIndicator(
            "CCI Expectations",
            str(cci_signal) if cci_signal else "N/A",
            "< 80",
            cci_active,
            "Consumer Confidence Expectations Index"
        ))
        
        # 5. Initial Jobless Claims (4-week MA)
        claims_signal = settings.get("jobless_claims", 0)
        claims_active = claims_signal > 400000
        indicators.append(MacroIndicator(
            "Jobless Claims (4W MA)",
            f"{claims_signal:,.0f}" if claims_signal else "N/A",
            "> 400,000",
            claims_active,
            "Initial Jobless Claims 4-week average"
        ))
        
        self.macro_indicators = indicators
        return indicators
    
    def check_macro_regime(self, settings, yield_spread=None):
        """檢查宏觀經濟週期
        
        Returns:
            Expansion: 0 signals active
            Peak: 1-2 signals active
            Contraction: 3+ signals active
            Trough: Manual judgment (requires manual override)
        """
        indicators = self.evaluate_macro_indicators(settings, yield_spread)
        
        active_count = sum(1 for ind in indicators if ind.is_active)
        
        # Manual trough override
        regime_override = settings.get("regime_override", None)
        if regime_override == "Trough":
            return "Trough"
        
        if active_count == 0:
            return "Expansion"
        elif active_count <= 2:
            return "Peak"
        else:
            return "Contraction"
    
    def get_regime_rules(self, macro_regime):
        """根據經濟週期返回可執行的規則
        
        Expansion (0 signals):
            - Rule 1 DCA: OK
            - Rule 2 Tactical Overlay: OK
            - Extra buys: OK
        
        Peak (1-2 signals):
            - Rule 1 DCA: OK
            - Rule 2 Tactical Overlay: PAUSED
            - Extra buys: OK
        
        Contraction (3+ signals):
            - Rule 1 DCA: OK (monthly minimum only)
            - Rule 2 Tactical Overlay: PAUSED
            - Extra buys: PAUSED
        
        Trough (manual):
            - Based on manual settings
        """
        rules = {
            "Expansion": {
                "rule1_dca": "OK",
                "rule2_tactical": "OK",
                "extra_buys": "OK",
                "description": "All rules active - DCA + Tactical Overlay both OK"
            },
            "Peak": {
                "rule1_dca": "OK",
                "rule2_tactical": "PAUSED",
                "extra_buys": "OK",
                "description": "Rule 1 DCA normal, Rule 2 Tactical paused"
            },
            "Contraction": {
                "rule1_dca": "OK (min only)",
                "rule2_tactical": "PAUSED",
                "extra_buys": "PAUSED",
                "description": "Only basic DCA with monthly minimum"
            },
            "Trough": {
                "rule1_dca": "OK",
                "rule2_tactical": "PAUSED",
                "extra_buys": "OK (gradual)",
                "description": "Gradual reopening - manual judgment required"
            }
        }
        
        return rules.get(macro_regime, rules["Expansion"])
    
    def check_cash_gate(self, current_cash_usd, cash_floor_usd):
        """檢查現金是否高於底線"""
        return current_cash_usd >= cash_floor_usd
    
    def evaluate_rule2_final(self, price_trigger, macro_regime, cash_above_floor, ai_risk=None):
        """最終 Rule 2 執行決定"""
        rules = self.get_regime_rules(macro_regime)
        
        if not price_trigger:
            return "No Trigger"
        
        if rules["rule2_tactical"] == "PAUSED":
            return f"Paused ({macro_regime})"
        
        if ai_risk and ai_risk.get("enabled") and ai_risk.get("is_active"):
            return f"AI Risk Active: {ai_risk.get('reason', 'Unknown')}"
        
        if not cash_above_floor:
            return "Blocked by Cash"
        
        return "Execute"
    
    def can_execute_rule1(self, macro_regime, is_extra_buy=False):
        """檢查 Rule 1 是否可執行"""
        rules = self.get_regime_rules(macro_regime)
        
        if is_extra_buy and rules["extra_buys"] == "PAUSED":
            return False, f"Extra buys paused ({macro_regime})"
        
        return True, "OK"
    
    def get_rule1_amount_limit(self, macro_regime, requested_amount, monthly_minimum):
        """根據經濟週期限制 Rule 1 投資金額"""
        rules = self.get_regime_rules(macro_regime)
        
        if rules["rule1_dca"] == "OK (min only)":
            # Contraction: only allow monthly minimum
            return min(requested_amount, monthly_minimum), "Limited to monthly minimum (Contraction)"
        
        return requested_amount, "OK"
