"""組合持倉管理"""
import json
import os
from datetime import datetime
from core.config import TARGET_WEIGHTS

class PortfolioManager:
    def __init__(self):
        self.holdings_file = "data/holdings.json"
        self.transactions_file = "data/transactions.json"
        self.holdings = self.load_holdings()
        self.transactions = self.load_transactions()
    
    def load_holdings(self):
        """載入持倉"""
        if os.path.exists(self.holdings_file):
            try:
                with open(self.holdings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_holdings(self):
        """儲存持倉"""
        os.makedirs("data", exist_ok=True)
        with open(self.holdings_file, 'w') as f:
            json.dump(self.holdings, f, indent=2, ensure_ascii=False)
    
    def load_transactions(self):
        """載入交易記錄"""
        if os.path.exists(self.transactions_file):
            try:
                with open(self.transactions_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_transactions(self):
        """儲存交易記錄"""
        os.makedirs("data", exist_ok=True)
        with open(self.transactions_file, 'w') as f:
            json.dump(self.transactions, f, indent=2, ensure_ascii=False)
    
    def get_holdings(self):
        """獲取持倉"""
        return self.holdings
    
    def get_holdings_with_current_value(self, prices):
        """獲取持倉 + 當前市值"""
        result = {}
        for ticker, holding in self.holdings.items():
            shares = holding.get('shares', 0)
            avg_cost = holding.get('avg_cost', 0)
            
            current_price = prices.get(ticker, 0)
            current_value = shares * current_price
            cost_basis = shares * avg_cost
            pnl = current_value - cost_basis
            pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            result[ticker] = {
                'shares': shares,
                'avg_cost': avg_cost,
                'cost_basis': cost_basis,
                'current_price': current_price,
                'current_value': current_value,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            }
        return result
    
    def initial_buy(self, investments, prices):
        """初始建倉
        
        Args:
            investments: dict {ticker: {'shares': ..., 'price': ...}}
            prices: dict {ticker: price}
        """
        for ticker, data in investments.items():
            shares = data.get('target_shares', 0)
            price = prices.get(ticker, 0)
            
            self.holdings[ticker] = {
                'shares': shares,
                'avg_cost': price
            }
            
            self.transactions.append({
                'date': datetime.now().isoformat(),
                'type': 'INITIAL_BUY',
                'ticker': ticker,
                'shares': shares,
                'price': price,
                'amount': shares * price
            })
        
        self.save_holdings()
        self.save_transactions()
    
    def execute_rule1_buy(self, investments, prices, rule_type):
        """執行 Rule 1 買入
        
        Args:
            investments: dict {ticker: {'amount_usd': ..., 'shares': ...}}
            prices: dict {ticker: price}
            rule_type: 'buy1' / 'buy2' / 'buy3' / 'fallback'
        """
        for ticker, data in investments.items():
            shares = data.get('shares', 0)
            price = prices.get(ticker, 0)
            
            if ticker in self.holdings:
                old_shares = self.holdings[ticker]['shares']
                old_cost = self.holdings[ticker]['avg_cost']
                new_shares = old_shares + shares
                new_avg_cost = (old_shares * old_cost + shares * price) / new_shares
                
                self.holdings[ticker] = {
                    'shares': new_shares,
                    'avg_cost': new_avg_cost
                }
            else:
                self.holdings[ticker] = {
                    'shares': shares,
                    'avg_cost': price
                }
            
            self.transactions.append({
                'date': datetime.now().isoformat(),
                'type': f'RULE1_{rule_type.upper()}',
                'ticker': ticker,
                'shares': shares,
                'price': price,
                'amount': shares * price
            })
        
        self.save_holdings()
        self.save_transactions()
    
    def execute_rule2_tactical(self, rule2_investments, prices):
        """執行 Rule 2 Tactical Overlay
        
        Args:
            rule2_investments: dict with 'sell_bnd_shares', 'iwy_shares', 'spmo_shares'
            prices: dict {ticker: price}
        """
        # 賣 BND
        if 'BND' in self.holdings and 'sell_bnd_shares' in rule2_investments:
            sell_shares = rule2_investments['sell_bnd_shares']
            bnd_price = prices.get('BND', 0)
            
            self.holdings['BND']['shares'] -= sell_shares
            
            self.transactions.append({
                'date': datetime.now().isoformat(),
                'type': 'RULE2_SELL_BND',
                'ticker': 'BND',
                'shares': -sell_shares,
                'price': bnd_price,
                'amount': -sell_shares * bnd_price
            })
        
        # 買 IWY
        if 'iwy_shares' in rule2_investments:
            iwy_shares = rule2_investments['iwy_shares']
            iwy_price = prices.get('IWY', 0)
            
            if 'IWY' in self.holdings:
                old_shares = self.holdings['IWY']['shares']
                old_cost = self.holdings['IWY']['avg_cost']
                new_shares = old_shares + iwy_shares
                new_avg_cost = (old_shares * old_cost + iwy_shares * iwy_price) / new_shares
                self.holdings['IWY'] = {'shares': new_shares, 'avg_cost': new_avg_cost}
            else:
                self.holdings['IWY'] = {'shares': iwy_shares, 'avg_cost': iwy_price}
            
            self.transactions.append({
                'date': datetime.now().isoformat(),
                'type': 'RULE2_BUY_IWY',
                'ticker': 'IWY',
                'shares': iwy_shares,
                'price': iwy_price,
                'amount': iwy_shares * iwy_price
            })
        
        # 買 SPMO
        if 'spmo_shares' in rule2_investments:
            spmo_shares = rule2_investments['spmo_shares']
            spmo_price = prices.get('SPMO', 0)
            
            if 'SPMO' in self.holdings:
                old_shares = self.holdings['SPMO']['shares']
                old_cost = self.holdings['SPMO']['avg_cost']
                new_shares = old_shares + spmo_shares
                new_avg_cost = (old_shares * old_cost + spmo_shares * spmo_price) / new_shares
                self.holdings['SPMO'] = {'shares': new_shares, 'avg_cost': new_avg_cost}
            else:
                self.holdings['SPMO'] = {'shares': spmo_shares, 'avg_cost': spmo_price}
            
            self.transactions.append({
                'date': datetime.now().isoformat(),
                'type': 'RULE2_BUY_SPMO',
                'ticker': 'SPMO',
                'shares': spmo_shares,
                'price': spmo_price,
                'amount': spmo_shares * spmo_price
            })
        
        self.save_holdings()
        self.save_transactions()
    
    def get_transactions(self):
        """獲取交易記錄"""
        return self.transactions
