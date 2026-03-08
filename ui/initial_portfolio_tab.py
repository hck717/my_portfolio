"""初始買入配置頁面"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLabel, QPushButton, QMessageBox)
from PySide6.QtCore import Qt

class InitialPortfolioTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("🚀 初始建倉配置 (Initial Portfolio)")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        desc = QLabel("根據目標配置與可投資金額，計算初始建倉需買入的每隻 ETF 股數。")
        desc.setStyleSheet("margin: 10px;")
        layout.addWidget(desc)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Ticker", "角色", "權重", "當前價格", "目標金額 (USD)", "建議買入股數"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.execute_btn = QPushButton("✅ 執行初始建倉")
        self.execute_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #4CAF50; color: white;")
        self.execute_btn.clicked.connect(self.execute_initial_buy)
        layout.addWidget(self.execute_btn)
    
    def update_display(self):
        from core.config import ETF_ROLES
        
        allocation = self.main_window.allocation
        self.table.setRowCount(len(allocation))
        
        row = 0
        for ticker, data in sorted(allocation.items()):
            self.table.setItem(row, 0, QTableWidgetItem(ticker))
            self.table.setItem(row, 1, QTableWidgetItem(ETF_ROLES.get(ticker, "")))
            self.table.setItem(row, 2, QTableWidgetItem(f"{data['weight']*100:.0f}%"))
            self.table.setItem(row, 3, QTableWidgetItem(f"${data['price']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"${data['target_value_usd']:,.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{data['target_shares']:.2f}"))
            row += 1
    
    def execute_initial_buy(self):
        reply = QMessageBox.question(
            self,
            "確認初始建倉",
            "確定要執行初始建倉？\n\n這會根據目標配置買入所有 6 隻 ETF。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.main_window.portfolio_manager.initial_buy(
                    self.main_window.allocation,
                    self.main_window.prices
                )
                
                QMessageBox.information(
                    self,
                    "建倉完成",
                    "初始建倉已完成！\n\n請到「當前持倉」頁面查看。"
                )
                
                self.main_window.update_all_tabs()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "錯誤",
                    f"初始建倉失敗：{str(e)}"
                )
