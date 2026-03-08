"""Portfolio calculation engine"""
from core.config import TARGET_WEIGHTS, WORKING_MODE_BASE

class PortfolioEngine:
    def __init__(self, data_service):
        self.data_service = data_service
    
    def calculate_estimated_dividends(self, current_assets_hkd, fx_rate, prices, ttm_dividends):
        """估算年度組合股息"""
        total_assets_usd = current_assets_hkd / fx_rate
        estimated_annual_div = 0.0
        
        for ticker, weight in TARGET_WEIGHTS.items():
            if ticker in prices and ticker in ttm_dividends:
                target_value = total_assets_usd * weight
                estimated_shares = target_value / prices[ticker]
                estimated_annual_div += estimated_shares * ttm_dividends[ticker]
        
        return estimated_annual_div
    
    def calculate_monthly_minimum(self, mode, estimated_annual_div):
        """計算每月最低投資額
        
        Working mode: 1000 USD + trailing dividends / 12
        Student mode: trailing dividends / 12 (但仍然有 minimum)
        """
        monthly_div = estimated_annual_div / 12.0
        
        if mode == "working":
            return WORKING_MODE_BASE + monthly_div
        else:  # student
            # Student mode 都要有 minimum，基於股息
            return monthly_div if monthly_div > 0 else 100  # 最少 100 USD
    
    def calculate_cash_targets(self, monthly_minimum):
        """計算現金目標、底線、上限"""
        target = 12 * monthly_minimum
        floor = 9 * monthly_minimum
        ceiling = 18 * monthly_minimum
        return target, floor, ceiling
    
    def calculate_investable_amount(self, current_assets_hkd, target_cash_hkd, extra_investable_usd, fx_rate):
        """計算最終可投資金額"""
        base_investable_hkd = current_assets_hkd - target_cash_hkd
        extra_investable_hkd = extra_investable_usd * fx_rate
        final_investable_hkd = base_investable_hkd + extra_investable_hkd
        final_investable_usd = final_investable_hkd / fx_rate
        return final_investable_hkd, final_investable_usd
    
    def calculate_allocation(self, investable_usd, prices):
        """計算每隻 ETF 目標配置"""
        allocation = {}
        
        for ticker, weight in TARGET_WEIGHTS.items():
            if ticker in prices:
                target_value_usd = investable_usd * weight
                target_shares = target_value_usd / prices[ticker]
                
                allocation[ticker] = {
                    "weight": weight,
                    "target_value_usd": target_value_usd,
                    "target_shares": target_shares,
                    "price": prices[ticker]
                }
        
        return allocation
