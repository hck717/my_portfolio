"""主控台頁面 - with validation"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
                               QComboBox, QLabel, QPushButton, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
from core.logger import logger

class DashboardTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Dashboard - Portfolio Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        btn_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("REFRESH DATA")
        self.refresh_btn.setStyleSheet("padding: 10px; font-weight: bold;")
        self.refresh_btn.clicked.connect(lambda: self.main_window.refresh_data())
        btn_layout.addWidget(self.refresh_btn)
        
        self.load_btn = QPushButton("FORCE RELOAD")
        self.load_btn.setStyleSheet("padding: 10px;")
        self.load_btn.clicked.connect(lambda: self.main_window.force_refresh_data())
        btn_layout.addWidget(self.load_btn)
        
        self.reset_btn = QPushButton("RESET ALL DATA")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.reset_btn.clicked.connect(lambda: self.main_window.reset_all_data())
        btn_layout.addWidget(self.reset_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        input_group = QGroupBox("Input Settings")
        input_layout = QFormLayout()
        input_group.setLayout(input_layout)
        
        self.assets_input = QLineEdit(str(self.main_window.settings["current_assets_hkd"]))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["working", "student"])
        self.mode_combo.setCurrentText(self.main_window.settings["mode"])
        self.extra_input = QLineEdit(str(self.main_window.settings["extra_investable_usd"]))
        self.fx_input = QLineEdit(str(self.main_window.settings["fx_rate"]))
        
        input_layout.addRow("Total Assets (HKD):", self.assets_input)
        input_layout.addRow("Mode:", self.mode_combo)
        input_layout.addRow("Extra Investable (USD):", self.extra_input)
        input_layout.addRow("USD/HKD Rate:", self.fx_input)
        
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
        
        calcs_layout.addRow("Est. Annual Div (USD):", self.est_div_label)
        calcs_layout.addRow("Monthly Min (USD):", self.monthly_min_label)
        calcs_layout.addRow("Target Cash (HKD/USD):", self.target_cash_label)
        calcs_layout.addRow("Floor Cash (HKD/USD):", self.floor_cash_label)
        calcs_layout.addRow("Ceiling Cash (HKD/USD):", self.ceiling_cash_label)
        calcs_layout.addRow("Investable (HKD/USD):", self.investable_label)
        
        layout.addWidget(calcs_group)
        layout.addStretch()
    
    def validate_inputs(self) -> tuple[bool, str]:
        """Validate all input fields"""
        try:
            assets = float(self.assets_input.text())
            if assets < 0:
                return False, "Total assets must be >= 0"
            if assets > 100000000:
                return False, "Total assets seems too high"
        except ValueError:
            return False, "Total assets must be a valid number"
        
        try:
            extra = float(self.extra_input.text())
            if extra < 0:
                return False, "Extra investable must be >= 0"
        except ValueError:
            return False, "Extra investable must be a valid number"
        
        try:
            fx_rate = float(self.fx_input.text())
            if fx_rate <= 0:
                return False, "FX rate must be > 0"
            if fx_rate > 20:
                return False, "FX rate seems too high"
        except ValueError:
            return False, "FX rate must be a valid number"
        
        mode = self.mode_combo.currentText()
        if mode not in ["working", "student"]:
            return False, "Invalid mode selected"
        
        return True, ""
    
    def save_settings(self):
        valid, error_msg = self.validate_inputs()
        
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            logger.warning(f"Input validation failed: {error_msg}")
            return
        
        try:
            self.main_window.settings["current_assets_hkd"] = float(self.assets_input.text())
            self.main_window.settings["mode"] = self.mode_combo.currentText()
            self.main_window.settings["extra_investable_usd"] = float(self.extra_input.text())
            self.main_window.settings["fx_rate"] = float(self.fx_input.text())
            
            self.main_window.save_settings()
            self.main_window.calculate_portfolio()
            self.main_window.update_all_tabs()
            
            logger.info("Settings saved successfully")
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
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
