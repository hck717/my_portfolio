"""Main application window"""
from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import QTimer
from core.data_service import DataService
from core.portfolio_engine import PortfolioEngine
from core.rules_engine import RulesEngine
from core.config import DEFAULT_SETTINGS, TICKERS
from ui.dashboard_tab import DashboardTab
from ui.allocation_tab import AllocationTab
from ui.rules_tab import RulesTab
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hi5 Portfolio Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        self.data_service = DataService()
        self.portfolio_engine = PortfolioEngine(self.data_service)
        self.rules_engine = RulesEngine(self.data_service)
        
        self.settings = self.load_settings()
        
        self.init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(60000)
        
        self.refresh_data()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.dashboard_tab = DashboardTab(self)
        self.allocation_tab = AllocationTab(self)
        self.rules_tab = RulesTab(self)
        
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.allocation_tab, "Allocation")
        self.tabs.addTab(self.rules_tab, "Rules")
        
        refresh_btn = QPushButton("Refresh Market Data")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
    
    def load_settings(self):
        settings_path = "data/settings.json"
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        os.makedirs("data", exist_ok=True)
        with open("data/settings.json", 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def refresh_data(self):
        try:
            self.prices = self.data_service.get_prices(TICKERS)
            self.ttm_dividends = self.data_service.get_ttm_dividends(TICKERS)
            
            self.rsp_yesterday = self.data_service.get_yesterday_close("RSP")
            self.rsp_monthly_high = self.data_service.get_monthly_high("RSP")
            
            self.iwy_40d_ago = self.data_service.get_close_n_days_ago("IWY", 40)
            self.spmo_40d_ago = self.data_service.get_close_n_days_ago("SPMO", 40)
            
            self.calculate_portfolio()
            self.update_all_tabs()
            
        except Exception as e:
            QMessageBox.warning(self, "Data Refresh Error", f"Failed to refresh data: {str(e)}")
    
    def calculate_portfolio(self):
        fx_rate = self.settings["fx_rate"]
        current_assets_hkd = self.settings["current_assets_hkd"]
        mode = self.settings["mode"]
        extra_investable_usd = self.settings["extra_investable_usd"]
        
        self.estimated_annual_div = self.portfolio_engine.calculate_estimated_dividends(
            current_assets_hkd, fx_rate, self.prices, self.ttm_dividends
        )
        
        self.monthly_minimum = self.portfolio_engine.calculate_monthly_minimum(
            mode, self.estimated_annual_div
        )
        
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
    
    def update_all_tabs(self):
        self.dashboard_tab.update_display()
        self.allocation_tab.update_display()
        self.rules_tab.update_display()
