"""Dashboard tab"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                               QComboBox, QLabel, QPushButton, QGroupBox)
from PySide6.QtCore import Qt

class DashboardTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        input_group = QGroupBox("Input Settings")
        input_layout = QFormLayout()
        input_group.setLayout(input_layout)
        
        self.assets_input = QLineEdit(str(self.main_window.settings["current_assets_hkd"]))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["working", "student"])
        self.mode_combo.setCurrentText(self.main_window.settings["mode"])
        self.extra_input = QLineEdit(str(self.main_window.settings["extra_investable_usd"]))
        self.fx_input = QLineEdit(str(self.main_window.settings["fx_rate"]))
        
        input_layout.addRow("Current Assets (HKD):", self.assets_input)
        input_layout.addRow("Mode:", self.mode_combo)
        input_layout.addRow("Extra Investable (USD):", self.extra_input)
        input_layout.addRow("USDHKD FX Rate:", self.fx_input)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        input_layout.addRow(save_btn)
        
        layout.addWidget(input_group)
        
        calcs_group = QGroupBox("Portfolio Calculations")
        calcs_layout = QFormLayout()
        calcs_group.setLayout(calcs_layout)
        
        self.est_div_label = QLabel()
        self.monthly_min_label = QLabel()
        self.target_cash_label = QLabel()
        self.floor_cash_label = QLabel()
        self.ceiling_cash_label = QLabel()
        self.investable_label = QLabel()
        
        calcs_layout.addRow("Estimated Annual Dividend (USD):", self.est_div_label)
        calcs_layout.addRow("Monthly Minimum Investment (USD):", self.monthly_min_label)
        calcs_layout.addRow("Target Cash (HKD / USD):", self.target_cash_label)
        calcs_layout.addRow("Cash Floor (HKD / USD):", self.floor_cash_label)
        calcs_layout.addRow("Cash Ceiling (HKD / USD):", self.ceiling_cash_label)
        calcs_layout.addRow("Final Investable Amount (HKD / USD):", self.investable_label)
        
        layout.addWidget(calcs_group)
        layout.addStretch()
    
    def save_settings(self):
        try:
            self.main_window.settings["current_assets_hkd"] = float(self.assets_input.text())
            self.main_window.settings["mode"] = self.mode_combo.currentText()
            self.main_window.settings["extra_investable_usd"] = float(self.extra_input.text())
            self.main_window.settings["fx_rate"] = float(self.fx_input.text())
            
            self.main_window.save_settings()
            self.main_window.calculate_portfolio()
            self.main_window.update_all_tabs()
        except ValueError:
            pass
    
    def update_display(self):
        self.est_div_label.setText(f"{self.main_window.estimated_annual_div:.2f}")
        self.monthly_min_label.setText(f"{self.main_window.monthly_minimum:.2f}")
        self.target_cash_label.setText(
            f"{self.main_window.target_cash_hkd:,.2f} / {self.main_window.target_cash_usd:,.2f}"
        )
        self.floor_cash_label.setText(
            f"{self.main_window.floor_cash_hkd:,.2f} / {self.main_window.floor_cash_usd:,.2f}"
        )
        self.ceiling_cash_label.setText(
            f"{self.main_window.ceiling_cash_hkd:,.2f} / {self.main_window.ceiling_cash_usd:,.2f}"
        )
        self.investable_label.setText(
            f"{self.main_window.investable_hkd:,.2f} / {self.main_window.investable_usd:,.2f}"
        )
