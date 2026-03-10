"""Backtesting service for strategy analysis"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from core.logger import logger
from core.config import TARGET_WEIGHTS, TICKERS

class BacktestResult:
    """Container for backtest results"""
    def __init__(self):
        self.total_return: float = 0.0
        self.annualized_return: float = 0.0
        self.annualized_volatility: float = 0.0
        self.sharpe_ratio: float = 0.0
        self.max_drawdown: float = 0.0
        self.trades: List[Dict] = []
        self.daily_values: pd.Series = None
        
    def to_dict(self) -> Dict:
        return {
            'total_return': self.total_return,
            'annualized_return': self.annualized_return,
            'annualized_volatility': self.annualized_volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'num_trades': len(self.trades)
        }

class BacktestEngine:
    """Backtesting engine for portfolio strategies"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
    
    def run_dca_backtest(self, 
                         tickers: List[str],
                         weights: Dict[str, float],
                         monthly_investment: float,
                         start_date: str,
                         end_date: str = None,
                         rule1_triggers: bool = True) -> BacktestResult:
        """Run DCA backtest with Rule 1 triggers"""
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        result = BacktestResult()
        
        try:
            prices = {}
            for ticker in tickers:
                data = yf.Ticker(ticker).history(start=start_date, end=end_date)
                if not data.empty:
                    prices[ticker] = data['Close']
            
            if not prices:
                logger.error("No price data fetched for backtest")
                return result
            
            prices_df = pd.DataFrame(prices)
            prices_df = prices_df.ffill()
            
            cash = self.initial_capital
            holdings = {t: 0 for t in tickers}
            trade_log = []
            
            dates = prices_df.index
            month = None
            
            for date in dates:
                current_month = date.month
                
                if current_month != month:
                    month = current_month
                    
                    invested = 0
                    for ticker in tickers:
                        if ticker in prices_df.columns:
                            amount = monthly_investment * weights.get(ticker, 0)
                            price = prices_df.loc[date, ticker]
                            
                            if price > 0:
                                shares = amount / price
                                holdings[ticker] += shares
                                invested += amount
                                
                                trade_log.append({
                                    'date': date.strftime('%Y-%m-%d'),
                                    'ticker': ticker,
                                    'shares': shares,
                                    'price': price,
                                    'amount': amount
                                })
                    
                    cash -= invested
                
                current_value = sum(
                    holdings[t] * prices_df.loc[date, t] 
                    for t in tickers 
                    if t in prices_df.columns
                )
                
                if result.daily_values is None:
                    result.daily_values = pd.Series([current_value + cash], index=[date])
                else:
                    result.daily_values[date] = current_value + cash
            
            if result.daily_values is not None and len(result.daily_values) > 1:
                returns = result.daily_values.pct_change().dropna()
                
                result.total_return = (result.daily_values.iloc[-1] / result.daily_values.iloc[0]) - 1
                result.annualized_return = returns.mean() * 252
                result.annualized_volatility = returns.std() * np.sqrt(252)
                result.sharpe_ratio = (result.annualized_return - 0.04) / result.annualized_volatility if result.annualized_volatility > 0 else 0
                
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.cummax()
                drawdown = (cumulative - running_max) / running_max
                result.max_drawdown = drawdown.min()
                
                result.trades = trade_log
            
            logger.info(f"Backtest complete: {result.total_return*100:.2f}% return")
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
        
        return result
    
    def compare_strategies(self,
                          tickers: List[str],
                          weights: Dict[str, float],
                          monthly_investment: float,
                          start_date: str,
                          end_date: str = None) -> Dict[str, BacktestResult]:
        """Compare different strategies"""
        
        strategies = {}
        
        logger.info("Running DCA strategy backtest...")
        strategies['DCA'] = self.run_dca_backtest(
            tickers, weights, monthly_investment, start_date, end_date
        )
        
        logger.info("Running lump sum strategy backtest...")
        lump_sum_result = BacktestResult()
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            prices = {}
            for ticker in tickers:
                data = yf.Ticker(ticker).history(start=start_date, end=end_date)
                if not data.empty:
                    prices[ticker] = data['Close']
            
            if prices:
                prices_df = pd.DataFrame(prices).ffill()
                
                for ticker in tickers:
                    if ticker in prices_df.columns:
                        amount = self.initial_capital * weights.get(ticker, 0)
                        price = prices_df.iloc[0, prices_df.columns.get_loc(ticker)]
                        shares = amount / price
                        lump_sum_result.trades.append({
                            'date': prices_df.index[0].strftime('%Y-%m-%d'),
                            'ticker': ticker,
                            'shares': shares,
                            'price': price,
                            'amount': amount
                        })
                
                initial_value = self.initial_capital
                final_value = sum(
                    lump_sum_result.trades[i]['shares'] * prices_df.iloc[-1, i]
                    for i, t in enumerate(tickers)
                    if t in prices_df.columns and i < len(lump_sum_result.trades)
                )
                
                lump_sum_result.daily_values = (1 + prices_df.pct_change()).cumprod() * self.initial_capital
                returns = lump_sum_result.daily_values.pct_change().dropna()
                
                lump_sum_result.total_return = final_value / initial_value - 1
                lump_sum_result.annualized_return = returns.mean() * 252
                lump_sum_result.annualized_volatility = returns.std() * np.sqrt(252)
                lump_sum_result.sharpe_ratio = (lump_sum_result.annualized_return - 0.04) / lump_sum_result.annualized_volatility if lump_sum_result.annualized_volatility > 0 else 0
                
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.cummax()
                drawdown = (cumulative - running_max) / running_max
                lump_sum_result.max_drawdown = drawdown.min()
                
        except Exception as e:
            logger.error(f"Lump sum backtest failed: {e}")
        
        strategies['Lump Sum'] = lump_sum_result
        
        return strategies
