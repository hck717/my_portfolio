"""當前持倉頁面 - with filters and export"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLabel, QPushButton, QComboBox, QLineEdit,
                               QGroupBox, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
from core.config import TARGET_WEIGHTS
from core.export_service import ExportService
from core.logger import logger

class HoldingsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Current Holdings")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        export_layout = QHBoxLayout()
        export_btn = QPushButton("Export Holdings to CSV")
        export_btn.clicked.connect(self.export_holdings)
        export_layout.addWidget(export_btn)
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.summary_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Ticker", "Shares", "Avg Cost", "Cost Basis", 
            "Current Price", "Current Value", "Actual Wgt", "Target Wgt", 
            "Deviation", "PnL (USD)", "PnL (%)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
    
    def export_holdings(self):
        try:
            holdings = self.main_window.portfolio_manager.get_holdings()
            prices = getattr(self.main_window, 'prices', {})
            
            filename = ExportService.export_holdings(holdings, prices)
            
            QMessageBox.information(self, "Export Complete", f"Exported to:\n{filename}")
            logger.info(f"Holdings exported to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to export holdings: {e}")
            QMessageBox.critical(self, "Export Error", str(e))
    
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
            actual_weight = data['current_value'] / total_value if total_value > 0 else 0
            target_weight = TARGET_WEIGHTS.get(ticker, 0)
            weight_deviation = actual_weight - target_weight
            
            self.table.setItem(row, 0, QTableWidgetItem(ticker))
            self.table.setItem(row, 1, QTableWidgetItem(f"{data['shares']:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"${data['avg_cost']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"${data['cost_basis']:,.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"${data['current_price']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"${data['current_value']:,.2f}"))
            
            total_cost += data['cost_basis']
            total_value += data['current_value']
            total_pnl += data['pnl']
            
            row += 1
        
        row = 0
        for ticker, data in sorted(holdings_data.items()):
            actual_weight = data['current_value'] / total_value if total_value > 0 else 0
            target_weight = TARGET_WEIGHTS.get(ticker, 0)
            weight_deviation = actual_weight - target_weight
            
            actual_weight_item = QTableWidgetItem(f"{actual_weight*100:.2f}%")
            target_weight_item = QTableWidgetItem(f"{target_weight*100:.0f}%")
            deviation_item = QTableWidgetItem(f"{weight_deviation*100:+.2f}%")
            
            if abs(weight_deviation) > 0.02:
                deviation_item.setForeground(Qt.red)
            else:
                deviation_item.setForeground(Qt.green)
            
            self.table.setItem(row, 6, actual_weight_item)
            self.table.setItem(row, 7, target_weight_item)
            self.table.setItem(row, 8, deviation_item)
            
            pnl_item = QTableWidgetItem(f"${data['pnl']:,.2f}")
            pnl_pct_item = QTableWidgetItem(f"{data['pnl_pct']:+.2f}%")
            
            if data['pnl'] > 0:
                pnl_item.setForeground(Qt.green)
                pnl_pct_item.setForeground(Qt.green)
            elif data['pnl'] < 0:
                pnl_item.setForeground(Qt.red)
                pnl_pct_item.setForeground(Qt.red)
            
            self.table.setItem(row, 9, pnl_item)
            self.table.setItem(row, 10, pnl_pct_item)
            
            row += 1
        
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        summary_text = f"""
        Total Cost: ${total_cost:,.2f} | Current Value: ${total_value:,.2f} | 
        Total PnL: ${total_pnl:,.2f} ({total_pnl_pct:+.2f}%)
        """
        
        self.summary_label.setText(summary_text)
