"""Allocation tab"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLabel)
from PySide6.QtCore import Qt
from core.config import ETF_ROLES

class AllocationTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("ETF Target Allocation")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Ticker", "Role", "Weight", "Price (USD)", "Target Value (USD)", "Target Shares"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
    
    def update_display(self):
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
