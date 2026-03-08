"""當前持倉頁面"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLabel, QPushButton)
from PySide6.QtCore import Qt

class HoldingsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("📊 當前持倉 (Current Holdings)")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.summary_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Ticker", "持有股數", "平均成本", "成本基礎", 
            "當前價格", "當前市值", "盈虧 (USD)", "盈虧 (%)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
    
    def update_display(self):
        holdings_data = self.main_window.portfolio_manager.get_holdings_with_current_value(
            self.main_window.prices
        )
        
        self.table.setRowCount(len(holdings_data))
        
        total_cost = 0
        total_value = 0
        total_pnl = 0
        
        row = 0
        for ticker, data in sorted(holdings_data.items()):
            self.table.setItem(row, 0, QTableWidgetItem(ticker))
            self.table.setItem(row, 1, QTableWidgetItem(f"{data['shares']:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"${data['avg_cost']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"${data['cost_basis']:,.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"${data['current_price']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"${data['current_value']:,.2f}"))
            
            pnl_item = QTableWidgetItem(f"${data['pnl']:,.2f}")
            pnl_pct_item = QTableWidgetItem(f"{data['pnl_pct']:+.2f}%")
            
            if data['pnl'] > 0:
                pnl_item.setForeground(Qt.green)
                pnl_pct_item.setForeground(Qt.green)
            elif data['pnl'] < 0:
                pnl_item.setForeground(Qt.red)
                pnl_pct_item.setForeground(Qt.red)
            
            self.table.setItem(row, 6, pnl_item)
            self.table.setItem(row, 7, pnl_pct_item)
            
            total_cost += data['cost_basis']
            total_value += data['current_value']
            total_pnl += data['pnl']
            
            row += 1
        
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        summary_text = f"""
        💰 總成本: ${total_cost:,.2f} | 📊 總市值: ${total_value:,.2f} | 
        📈 總盈虧: ${total_pnl:,.2f} ({total_pnl_pct:+.2f}%)
        """
        
        self.summary_label.setText(summary_text)
