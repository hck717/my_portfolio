"""主視窗 - 整合所有功能"""
from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import QTimer
from core.data_service import DataService
from core.macro_data_service import MacroDataService
from core.portfolio_engine import PortfolioEngine
from core.portfolio_manager import PortfolioManager
from core.rules_engine import RulesEngine
from core.config import DEFAULT_SETTINGS, TICKERS
from ui.dashboard_tab import DashboardTab
from ui.allocation_tab import AllocationTab
from ui.rules_tab import RulesTab
from ui.strategy_tab import StrategyTab
from ui.holdings_tab import HoldingsTab
from ui.initial_portfolio_tab import InitialPortfolioTab
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hi5 組合管理系統")
        self.setGeometry(100, 100, 1400, 900)
        
        self.data_service = DataService()
        self.macro_service = MacroDataService()
        self.portfolio_engine = PortfolioEngine(self.data_service)
        self.portfolio_manager = PortfolioManager()
        self.rules_engine = RulesEngine(self.data_service)
        
        self.settings = self.load_settings()
        
        self.init_ui()
        
        # Auto-refresh 每 60 秒
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
        self.holdings_tab = HoldingsTab(self)
        self.initial_portfolio_tab = InitialPortfolioTab(self)
        self.allocation_tab = AllocationTab(self)
        self.rules_tab = RulesTab(self)
        self.strategy_tab = StrategyTab(self)
        
        self.tabs.addTab(self.dashboard_tab, "📊 主控台")
        self.tabs.addTab(self.holdings_tab, "💼 當前持倉")
        self.tabs.addTab(self.initial_portfolio_tab, "🚀 初始建倉")
        self.tabs.addTab(self.allocation_tab, "🎯 目標配置")
        self.tabs.addTab(self.rules_tab, "⚙️ 規則")
        self.tabs.addTab(self.strategy_tab, "📋 策略")
        
        refresh_btn = QPushButton("🔄 重新整理市場數據")
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
            json.dump(self.settings, f, indent=2, ensure_ascii=False)
    
    def refresh_data(self):
        try:
            print("\n=== Refreshing Data ===")
            
            # 抓 ETF 價格同股息
            print("Fetching ETF prices...")
            self.prices = self.data_service.get_prices(TICKERS)
            print(f"Prices: {self.prices}")
            
            print("Fetching ETF dividends...")
            self.ttm_dividends = self.data_service.get_ttm_dividends(TICKERS)
            print(f"Dividends: {self.ttm_dividends}")
            
            # 抓 RSP 數據（Rule 1）
            self.rsp_yesterday = self.data_service.get_yesterday_close("RSP")
            self.rsp_monthly_high = self.data_service.get_monthly_high("RSP")
            
            # 抓 IWY / SPMO 40D 數據（Rule 2）
            self.iwy_40d_ago = self.data_service.get_close_n_days_ago("IWY", 40)
            self.spmo_40d_ago = self.data_service.get_close_n_days_ago("SPMO", 40)
            
            # 抓宏觀指標
            macro_signals = self.macro_service.get_all_signals()
            self.settings['yield_curve_inverted'] = macro_signals['yield_curve_inverted']
            self.yield_spread = macro_signals['yield_spread']
            
            self.calculate_portfolio()
            self.calculate_investments()
            self.update_all_tabs()
            
            print("=== Refresh Complete ===")
            
        except Exception as e:
            print(f"Error in refresh_data: {e}")
            QMessageBox.warning(self, "數據重新整理錯誤", f"無法重新整理數據：{str(e)}")
    
    def calculate_portfolio(self):
        fx_rate = self.settings["fx_rate"]
        current_assets_hkd = self.settings["current_assets_hkd"]
        mode = self.settings["mode"]
        extra_investable_usd = self.settings["extra_investable_usd"]
        
        self.estimated_annual_div = self.portfolio_engine.calculate_estimated_dividends(
            current_assets_hkd, fx_rate, self.prices, self.ttm_dividends
        )
        
        print(f"Estimated annual dividend: {self.estimated_annual_div}")
        
        self.monthly_minimum = self.portfolio_engine.calculate_monthly_minimum(
            mode, self.estimated_annual_div
        )
        
        print(f"Monthly minimum: {self.monthly_minimum}")
        
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
        """計算各規則觸發時的投資金額"""
        # Rule 1 investments
        self.rule1_investments = self.rules_engine.calculate_rule1_investments(
            self.monthly_minimum, self.prices
        )
        
        # Rule 2 investments (使用目標配置中的 BND 市值)
        bnd_target_value = self.allocation.get("BND", {}).get("target_value_usd", 0)
        self.rule2_investments = self.rules_engine.calculate_rule2_investments(
            bnd_target_value, self.prices
        )
    
    def update_all_tabs(self):
        self.dashboard_tab.update_display()
        self.holdings_tab.update_display()
        self.initial_portfolio_tab.update_display()
        self.allocation_tab.update_display()
        self.rules_tab.update_display()
