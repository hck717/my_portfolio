"""組合表現分析"""
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

class PerformanceAnalyzer:
    def __init__(self, portfolio_manager, data_service):
        self.portfolio_manager = portfolio_manager
        self.data_service = data_service
    
    def get_portfolio_returns(self, start_date=None, end_date=None):
        """獲取組合歷史回報"""
        holdings = self.portfolio_manager.get_holdings()
        
        if not holdings:
            return pd.Series(dtype=float)
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 獲取每隻 ETF 歷史價格
        portfolio_values = None
        
        for ticker, holding in holdings.items():
            shares = holding['shares']
            
            try:
                hist = yf.Ticker(ticker).history(start=start_date, end=end_date)
                if not hist.empty:
                    ticker_values = hist['Close'] * shares
                    
                    if portfolio_values is None:
                        portfolio_values = ticker_values
                    else:
                        portfolio_values = portfolio_values.add(ticker_values, fill_value=0)
            except:
                pass
        
        if portfolio_values is None or portfolio_values.empty:
            return pd.Series(dtype=float)
        
        # 計算回報
        returns = portfolio_values.pct_change().dropna()
        return returns
    
    def get_benchmark_returns(self, benchmark='SPY', start_date=None, end_date=None):
        """獲取 benchmark 歷史回報"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            hist = yf.Ticker(benchmark).history(start=start_date, end=end_date)
            if not hist.empty:
                returns = hist['Close'].pct_change().dropna()
                return returns
        except:
            pass
        
        return pd.Series(dtype=float)
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.04):
        """計算 Sharpe Ratio"""
        if returns.empty or len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        sharpe = np.sqrt(252) * excess_returns.mean() / returns.std()
        return sharpe
    
    def calculate_sortino_ratio(self, returns, risk_free_rate=0.04):
        """計算 Sortino Ratio"""
        if returns.empty or len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return 0.0
        
        downside_std = downside_returns.std()
        if downside_std == 0:
            return 0.0
        
        sortino = np.sqrt(252) * excess_returns.mean() / downside_std
        return sortino
    
    def calculate_max_drawdown(self, returns):
        """計算最大回撤"""
        if returns.empty:
            return 0.0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        return max_dd
    
    def calculate_var(self, returns, confidence_level=0.95):
        """計算 Value at Risk (VaR)"""
        if returns.empty:
            return 0.0
        
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return var
    
    def calculate_cvar(self, returns, confidence_level=0.95):
        """計算 Conditional VaR (CVaR / Expected Shortfall)"""
        if returns.empty:
            return 0.0
        
        var = self.calculate_var(returns, confidence_level)
        cvar = returns[returns <= var].mean()
        return cvar
    
    def calculate_beta(self, portfolio_returns, benchmark_returns):
        """計算 Beta"""
        if portfolio_returns.empty or benchmark_returns.empty:
            return 0.0
        
        # Align indices
        aligned = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned) < 2:
            return 0.0
        
        covariance = aligned['portfolio'].cov(aligned['benchmark'])
        benchmark_variance = aligned['benchmark'].var()
        
        if benchmark_variance == 0:
            return 0.0
        
        beta = covariance / benchmark_variance
        return beta
    
    def calculate_alpha(self, portfolio_returns, benchmark_returns, risk_free_rate=0.04):
        """計算 Alpha"""
        if portfolio_returns.empty or benchmark_returns.empty:
            return 0.0
        
        beta = self.calculate_beta(portfolio_returns, benchmark_returns)
        
        portfolio_return = portfolio_returns.mean() * 252
        benchmark_return = benchmark_returns.mean() * 252
        
        alpha = portfolio_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))
        return alpha
    
    def get_performance_metrics(self, benchmark='SPY', start_date=None, end_date=None):
        """獲取完整表現指標"""
        portfolio_returns = self.get_portfolio_returns(start_date, end_date)
        benchmark_returns = self.get_benchmark_returns(benchmark, start_date, end_date)
        
        if portfolio_returns.empty:
            return None
        
        metrics = {
            'total_return': (1 + portfolio_returns).prod() - 1,
            'annualized_return': portfolio_returns.mean() * 252,
            'annualized_volatility': portfolio_returns.std() * np.sqrt(252),
            'sharpe_ratio': self.calculate_sharpe_ratio(portfolio_returns),
            'sortino_ratio': self.calculate_sortino_ratio(portfolio_returns),
            'max_drawdown': self.calculate_max_drawdown(portfolio_returns),
            'var_95': self.calculate_var(portfolio_returns, 0.95),
            'cvar_95': self.calculate_cvar(portfolio_returns, 0.95),
        }
        
        if not benchmark_returns.empty:
            metrics['beta'] = self.calculate_beta(portfolio_returns, benchmark_returns)
            metrics['alpha'] = self.calculate_alpha(portfolio_returns, benchmark_returns)
            metrics['benchmark_return'] = (1 + benchmark_returns).prod() - 1
        
        return metrics
