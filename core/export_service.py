"""Export service for CSV reports"""
import csv
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from core.logger import logger

class ExportService:
    """Service for exporting data to CSV"""
    
    EXPORT_DIR = Path("exports")
    EXPORT_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def export_holdings(cls, holdings: Dict[str, Any], prices: Dict[str, float]) -> str:
        """Export holdings to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = cls.EXPORT_DIR / f"holdings_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Ticker', 'Shares', 'Avg Cost', 'Current Price', 
                               'Current Value', 'Cost Basis', 'PnL', 'PnL %'])
                
                for ticker, holding in holdings.items():
                    shares = holding.get('shares', 0)
                    avg_cost = holding.get('avg_cost', 0)
                    current_price = prices.get(ticker, 0)
                    current_value = shares * current_price
                    cost_basis = shares * avg_cost
                    pnl = current_value - cost_basis
                    pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
                    
                    writer.writerow([
                        ticker,
                        f"{shares:.4f}",
                        f"${avg_cost:.2f}",
                        f"${current_price:.2f}",
                        f"${current_value:.2f}",
                        f"${cost_basis:.2f}",
                        f"${pnl:.2f}",
                        f"{pnl_pct:.2f}%"
                    ])
            
            logger.info(f"Holdings exported to {filename}")
            return str(filename)
        except Exception as e:
            logger.error(f"Failed to export holdings: {e}")
            raise
    
    @classmethod
    def export_transactions(cls, transactions: List[Dict[str, Any]], 
                          filter_type: str = None,
                          filter_ticker: str = None,
                          start_date: str = None,
                          end_date: str = None) -> str:
        """Export transactions to CSV with optional filters"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = cls.EXPORT_DIR / f"transactions_{timestamp}.csv"
        
        try:
            filtered = transactions
            
            if filter_type:
                filtered = [t for t in filtered if t.get('type') == filter_type]
            
            if filter_ticker:
                filtered = [t for t in filtered if t.get('ticker') == filter_ticker]
            
            if start_date:
                filtered = [t for t in filtered if t.get('date', '') >= start_date]
            
            if end_date:
                filtered = [t for t in filtered if t.get('date', '') <= end_date]
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Type', 'Ticker', 'Shares', 'Price', 'Amount'])
                
                for t in filtered:
                    writer.writerow([
                        t.get('date', ''),
                        t.get('type', ''),
                        t.get('ticker', ''),
                        f"{t.get('shares', 0):.4f}",
                        f"${t.get('price', 0):.2f}",
                        f"${t.get('amount', 0):.2f}"
                    ])
            
            logger.info(f"Transactions exported to {filename} ({len(filtered)} records)")
            return str(filename)
        except Exception as e:
            logger.error(f"Failed to export transactions: {e}")
            raise
    
    @classmethod
    def export_performance(cls, metrics: Dict[str, Any], benchmark: str = 'SPY') -> str:
        """Export performance metrics to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = cls.EXPORT_DIR / f"performance_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                
                for key, value in metrics.items():
                    if isinstance(value, float):
                        if 'return' in key or 'drawdown' in key or 'var' in key or 'cvar' in key:
                            writer.writerow([key, f"{value*100:.2f}%"])
                        elif 'volatility' in key:
                            writer.writerow([key, f"{value*100:.2f}%"])
                        elif 'sharpe' in key or 'sortino' in key or 'beta' in key:
                            writer.writerow([key, f"{value:.3f}"])
                        else:
                            writer.writerow([key, f"{value:.2f}"])
                    else:
                        writer.writerow([key, str(value)])
            
            logger.info(f"Performance exported to {filename}")
            return str(filename)
        except Exception as e:
            logger.error(f"Failed to export performance: {e}")
            raise
    
    @classmethod
    def export_all(cls, holdings: Dict, prices: Dict, 
                  transactions: List, metrics: Dict) -> List[str]:
        """Export all data to CSV files"""
        files = []
        
        try:
            files.append(cls.export_holdings(holdings, prices))
        except:
            pass
        
        try:
            files.append(cls.export_transactions(transactions))
        except:
            pass
        
        try:
            files.append(cls.export_performance(metrics))
        except:
            pass
        
        return files
