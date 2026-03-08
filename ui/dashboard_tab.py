"""主控台頁面"""
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
        
        # 輸入設定
        input_group = QGroupBox("📝 輸入設定")
        input_layout = QFormLayout()
        input_group.setLayout(input_layout)
        
        self.assets_input = QLineEdit(str(self.main_window.settings["current_assets_hkd"]))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["working", "student"])
        self.mode_combo.setCurrentText(self.main_window.settings["mode"])
        self.extra_input = QLineEdit(str(self.main_window.settings["extra_investable_usd"]))
        self.fx_input = QLineEdit(str(self.main_window.settings["fx_rate"]))
        
        input_layout.addRow("💰 總資產 (HKD):", self.assets_input)
        input_layout.addRow("👤 模式:", self.mode_combo)
        input_layout.addRow("🔺 額外可投資 (USD):", self.extra_input)
        input_layout.addRow("💱 USDHKD 匯率:", self.fx_input)
        
        save_btn = QPushButton("✅ 儲存設定")
        save_btn.clicked.connect(self.save_settings)
        input_layout.addRow(save_btn)
        
        layout.addWidget(input_group)
        
        # 組合計算
        calcs_group = QGroupBox("📊 組合計算")
        calcs_layout = QFormLayout()
        calcs_group.setLayout(calcs_layout)
        
        self.est_div_label = QLabel()
        self.monthly_min_label = QLabel()
        self.target_cash_label = QLabel()
        self.floor_cash_label = QLabel()
        self.ceiling_cash_label = QLabel()
        self.investable_label = QLabel()
        
        calcs_layout.addRow("💵 估算年度股息 (USD):", self.est_div_label)
        calcs_layout.addRow("📈 每月最低投資額 (USD):", self.monthly_min_label)
        calcs_layout.addRow("🎯 目標現金 (HKD / USD):", self.target_cash_label)
        calcs_layout.addRow("⚠️ 現金底線 (HKD / USD):", self.floor_cash_label)
        calcs_layout.addRow("🔺 現金上限 (HKD / USD):", self.ceiling_cash_label)
        calcs_layout.addRow("💼 最終可投資金額 (HKD / USD):", self.investable_label)
        
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
