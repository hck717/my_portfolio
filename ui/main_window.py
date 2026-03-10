"""主視窗 - 整合所有功能"""
from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                               QPushButton, QMessageBox, QHBoxLayout, QInputDialog, 
                               QLineEdit, QScrollArea)
from PySide6.QtCore import QTimer, Qt
from core.data_service import DataService
from core.macro_data_service import MacroDataService
from core.portfolio_engine import PortfolioEngine
from core.portfolio_manager import PortfolioManager
from core.performance_analyzer import PerformanceAnalyzer
from core.rules_engine import RulesEngine
from core.config import DEFAULT_SETTINGS, TICKERS
from core.logger import logger
from core.env_config import get_config
from core.notification_service import send_notification, send_rule1_alert, send_rule2_alert
from ui.dashboard_tab import DashboardTab
from ui.allocation_tab import AllocationTab
from ui.rules_tab import RulesTab
from ui.strategy_tab import StrategyTab
from ui.holdings_tab import HoldingsTab
from ui.initial_portfolio_tab import InitialPortfolioTab
from ui.performance_tab import PerformanceTab
import json
import os

config = get_config()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hi5 組合管理系統")
        self.setGeometry(100, 100, 1400, 900)
        
        logger.info("Initializing Hi5 Portfolio Manager")
        
        self.data_service = DataService()
        self.macro_service = MacroDataService()
        self.portfolio_engine = PortfolioEngine(self.data_service)
        self.portfolio_manager = PortfolioManager()
        self.performance_analyzer = PerformanceAnalyzer(self.portfolio_manager, self.data_service)
        self.rules_engine = RulesEngine(self.data_service)
        
        self.settings = self.load_settings()
        
        self.init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(config.REFRESH_INTERVAL_SECONDS * 1000)
        
        logger.info("Starting initial data refresh")
        self.refresh_data()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.dashboard_tab = DashboardTab(self)
        self.holdings_tab = HoldingsTab(self)
        self.performance_tab = PerformanceTab(self)
        self.initial_portfolio_tab = InitialPortfolioTab(self)
        self.allocation_tab = AllocationTab(self)
        self.rules_tab = RulesTab(self)
        self.strategy_tab = StrategyTab(self)
        
        self.tabs.addTab(self.create_scrollable_tab(self.dashboard_tab), "Dashboard")
        self.tabs.addTab(self.create_scrollable_tab(self.holdings_tab), "Holdings")
        self.tabs.addTab(self.create_scrollable_tab(self.performance_tab), "Performance")
        self.tabs.addTab(self.create_scrollable_tab(self.initial_portfolio_tab), "Initial")
        self.tabs.addTab(self.create_scrollable_tab(self.allocation_tab), "Allocation")
        self.tabs.addTab(self.create_scrollable_tab(self.rules_tab), "Rules")
        self.tabs.addTab(self.create_scrollable_tab(self.strategy_tab), "Strategy")
    
    def create_scrollable_tab(self, widget):
        """Wrap widget in scroll area"""
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        return scroll
    
    def load_settings(self):
        settings_path = "data/settings.json"
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
        return DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        os.makedirs("data", exist_ok=True)
        with open("data/settings.json", 'w') as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)
    
    def force_refresh_data(self):
        """Force refresh data by clearing cache"""
        logger.info("Force refreshing data - clearing cache")
        self.data_service.clear_cache()
        self.refresh_data()
    
    def reset_all_data(self):
        """Reset all data with verification"""
        reply = QMessageBox.warning(
            self,
            "Confirm Reset",
            "This will delete ALL holdings and transaction records!\n\nType 'RESET' to confirm:",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            text, ok = QInputDialog.getText(
                self,
                "Verification",
                "Enter 'RESET' to confirm deletion:"
            )
            
            if ok and text.upper() == "RESET":
                try:
                    if os.path.exists("data/holdings.json"):
                        os.remove("data/holdings.json")
                    if os.path.exists("data/transactions.json"):
                        os.remove("data/transactions.json")
                    logger.warning("All data has been reset by user")
                    
                    send_notification("Data Reset", "All portfolio data has been cleared")
                    
                    QMessageBox.information(
                        self,
                        "Reset Complete",
                        "All data has been deleted!"
                    )
                    
                    self.portfolio_manager.holdings = {}
                    self.portfolio_manager.transactions = []
                    self.update_all_tabs()
                    
                except Exception as e:
                    logger.error(f"Failed to reset data: {e}")
                    QMessageBox.critical(self, "Error", f"Reset failed: {str(e)}")
            else:
                QMessageBox.information(self, "Cancelled", "Verification code incorrect, reset cancelled")
    
    def refresh_data(self):
        try:
            logger.info("=== Refreshing Data ===")
            
            if not self.data_service.is_online():
                logger.warning("Offline mode - using cached data")
                QMessageBox.warning(self, "離線模式", "網絡不可用，將使用緩存數據")
            
            logger.info("Fetching ETF prices...")
            self.prices = self.data_service.get_prices(TICKERS)
            logger.info(f"Prices fetched: {len(self.prices)} tickers")
            
            logger.info("Fetching ETF dividends...")
            self.ttm_dividends = self.data_service.get_ttm_dividends(TICKERS)
            logger.info(f"Dividends fetched: {self.ttm_dividends}")
            
            self.rsp_yesterday = self.data_service.get_yesterday_close("RSP")
            self.rsp_monthly_high = self.data_service.get_monthly_high("RSP")
            
            self.iwy_40d_ago = self.data_service.get_close_n_days_ago("IWY", 40)
            self.spmo_40d_ago = self.data_service.get_close_n_days_ago("SPMO", 40)
            
            macro_signals = self.macro_service.get_all_signals()
            self.settings['yield_curve_inverted'] = macro_signals['yield_curve_inverted']
            self.yield_spread = macro_signals['yield_spread']
            
            self.calculate_portfolio()
            self.calculate_investments()
            self.check_rule_triggers()
            self.update_all_tabs()
            
            logger.info("=== Refresh Complete ===")
            
        except Exception as e:
            logger.error(f"Error in refresh_data: {e}")
            QMessageBox.warning(self, "數據重新整理錯誤", f"無法重新整理數據：{str(e)}")
    
    def check_rule_triggers(self):
        """Check if any rules are triggered and send notifications"""
        if "RSP" not in self.prices:
            return
        
        rsp_price = self.prices["RSP"]
        
        triggers = self.rules_engine.check_rule1_triggers(
            rsp_price, self.rsp_yesterday, self.rsp_monthly_high
        )
        
        if any(triggers.values()):
            logger.info(f"Rule 1 triggers detected: {triggers}")
            send_rule1_alert("Rule 1 DCA", triggers)
        
        if "IWY" in self.prices and "SPMO" in self.prices:
            triggered, _, _ = self.rules_engine.check_rule2_trigger(
                self.prices["IWY"], self.iwy_40d_ago,
                self.prices["SPMO"], self.spmo_40d_ago
            )
            
            if triggered:
                logger.info("Rule 2 tactical trigger detected")
                send_rule2_alert(True)
    
    def calculate_portfolio(self):
        fx_rate = self.settings["fx_rate"]
        current_assets_hkd = self.settings["current_assets_hkd"]
        mode = self.settings["mode"]
        extra_investable_usd = self.settings["extra_investable_usd"]
        
        self.estimated_annual_div = self.portfolio_engine.calculate_estimated_dividends(
            current_assets_hkd, fx_rate, self.prices, self.ttm_dividends
        )
        
        logger.info(f"Estimated annual dividend: {self.estimated_annual_div}")
        
        self.monthly_minimum = self.portfolio_engine.calculate_monthly_minimum(
            mode, self.estimated_annual_div
        )
        
        logger.info(f"Monthly minimum: {self.monthly_minimum}")
        
        self.target_cash_usd, self.floor_cash_usd, self.ceiling_cash_usd = \
            self.portfolio_engine.calculate_cash_targets(self.monthly_minimum)
        
        self.target_cash_hkd = self.target_cash_usd * fx_rate
        self.floor_cash_hkd = self.floor_cash_usd * fx_rate
        self.ceiling_cash_hkd = self.ceiling_cash_usd * fx_rate
        
        self.investable_hkd, self.investable_usd = \
            self.portfolio_engine.calculate_investable_amount(
                current_assets_hkd, self.target_cash_hkd, extra_investable_usd, fx_rate
            )
        
        self.allocation = self.portfolio_engine.calculate_allocation(
            self.investable_usd, self.prices
        )
    
    def calculate_investments(self):
        self.rule1_investments = self.rules_engine.calculate_rule1_investments(
            self.monthly_minimum, self.prices
        )
        
        bnd_target_value = self.allocation.get("BND", {}).get("target_value_usd", 0)
        self.rule2_investments = self.rules_engine.calculate_rule2_investments(
            bnd_target_value, self.prices
        )
    
    def update_all_tabs(self):
        self.dashboard_tab.update_display()
        self.holdings_tab.update_display()
        self.performance_tab.update_display()
        self.initial_portfolio_tab.update_display()
        self.allocation_tab.update_display()
        self.rules_tab.update_display()
