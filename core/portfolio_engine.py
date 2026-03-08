"""Portfolio calculation engine"""
from core.config import TARGET_WEIGHTS, WORKING_MODE_BASE

class PortfolioEngine:
    def __init__(self, data_service):
        self.data_service = data_service
    
    def calculate_estimated_dividends(self, current_assets_hkd, fx_rate, prices, ttm_dividends):
        """Estimate annual portfolio dividends"""
        total_assets_usd = current_assets_hkd / fx_rate
        estimated_annual_div = 0.0
        
        for ticker, weight in TARGET_WEIGHTS.items():
            if ticker in prices and ticker in ttm_dividends:
                target_value = total_assets_usd * weight
                estimated_shares = target_value / prices[ticker]
                estimated_annual_div += estimated_shares * ttm_dividends[ticker]
        
        return estimated_annual_div
    
    def calculate_monthly_minimum(self, mode, estimated_annual_div):
        """Calculate monthly minimum investment amount"""
        if mode == "working":
            return WORKING_MODE_BASE + estimated_annual_div / 12.0
        else:
            return estimated_annual_div / 12.0
    
    def calculate_cash_targets(self, monthly_minimum):
        """Calculate cash target, floor, ceiling"""
        target = 12 * monthly_minimum
        floor = 9 * monthly_minimum
        ceiling = 18 * monthly_minimum
        return target, floor, ceiling
    
    def calculate_investable_amount(self, current_assets_hkd, target_cash_hkd, extra_investable_usd, fx_rate):
        """Calculate final investable amount"""
        base_investable_hkd = current_assets_hkd - target_cash_hkd
        extra_investable_hkd = extra_investable_usd * fx_rate
        final_investable_hkd = base_investable_hkd + extra_investable_hkd
        final_investable_usd = final_investable_hkd / fx_rate
        return final_investable_hkd, final_investable_usd
    
    def calculate_allocation(self, investable_usd, prices):
        """Calculate target allocation for each ETF"""
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
