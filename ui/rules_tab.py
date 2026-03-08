"""Rules tab"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                               QGroupBox, QSpinBox, QPushButton)
from PySide6.QtCore import Qt

class RulesTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        rule1_group = QGroupBox("Rule 1 - DCA Triggers")
        rule1_layout = QFormLayout()
        rule1_group.setLayout(rule1_layout)
        
        self.rsp_price_label = QLabel()
        self.rsp_yesterday_label = QLabel()
        self.rsp_daily_change_label = QLabel()
        self.rsp_monthly_high_label = QLabel()
        self.rsp_monthly_dd_label = QLabel()
        self.buy1_label = QLabel()
        self.buy2_label = QLabel()
        self.buy3_label = QLabel()
        self.fallback_label = QLabel()
        
        rule1_layout.addRow("RSP Current Price:", self.rsp_price_label)
        rule1_layout.addRow("RSP Yesterday Close:", self.rsp_yesterday_label)
        rule1_layout.addRow("RSP Daily Change:", self.rsp_daily_change_label)
        rule1_layout.addRow("RSP Monthly High:", self.rsp_monthly_high_label)
        rule1_layout.addRow("RSP Monthly Drawdown:", self.rsp_monthly_dd_label)
        rule1_layout.addRow("Buy1 Trigger (>= -1%):", self.buy1_label)
        rule1_layout.addRow("Buy2 Trigger (>= -5%):", self.buy2_label)
        rule1_layout.addRow("Buy3 Trigger (>= -10%):", self.buy3_label)
        rule1_layout.addRow("3rd Friday Fallback:", self.fallback_label)
        
        layout.addWidget(rule1_group)
        
        rule2_group = QGroupBox("Rule 2 - Tactical Overlay")
        rule2_layout = QFormLayout()
        rule2_group.setLayout(rule2_layout)
        
        self.iwy_price_label = QLabel()
        self.iwy_40d_label = QLabel()
        self.iwy_return_label = QLabel()
        self.spmo_price_label = QLabel()
        self.spmo_40d_label = QLabel()
        self.spmo_return_label = QLabel()
        self.price_trigger_label = QLabel()
        
        rule2_layout.addRow("IWY Current:", self.iwy_price_label)
        rule2_layout.addRow("IWY 40D Ago:", self.iwy_40d_label)
        rule2_layout.addRow("IWY 40D Return:", self.iwy_return_label)
        rule2_layout.addRow("SPMO Current:", self.spmo_price_label)
        rule2_layout.addRow("SPMO 40D Ago:", self.spmo_40d_label)
        rule2_layout.addRow("SPMO 40D Return:", self.spmo_return_label)
        rule2_layout.addRow("Price Trigger:", self.price_trigger_label)
        
        layout.addWidget(rule2_group)
        
        macro_group = QGroupBox("Macro Risk Gate")
        macro_layout = QFormLayout()
        macro_group.setLayout(macro_layout)
        
        self.lei_input = QSpinBox()
        self.lei_input.setRange(0, 1)
        self.lei_input.setValue(self.main_window.settings["lei_signal"])
        
        self.yield_curve_input = QSpinBox()
        self.yield_curve_input.setRange(0, 1)
        self.yield_curve_input.setValue(self.main_window.settings["yield_curve_inverted"])
        
        self.sahm_input = QSpinBox()
        self.sahm_input.setRange(0, 1)
        self.sahm_input.setValue(self.main_window.settings["sahm_rule_signal"])
        
        macro_layout.addRow("LEI Signal (0/1):", self.lei_input)
        macro_layout.addRow("10Y-3M Inverted (0/1):", self.yield_curve_input)
        macro_layout.addRow("Sahm Rule Signal (0/1):", self.sahm_input)
        
        save_macro_btn = QPushButton("Save Macro Signals")
        save_macro_btn.clicked.connect(self.save_macro_signals)
        macro_layout.addRow(save_macro_btn)
        
        self.macro_regime_label = QLabel()
        self.cash_gate_label = QLabel()
        self.rule2_final_label = QLabel()
        
        macro_layout.addRow("Macro Regime:", self.macro_regime_label)
        macro_layout.addRow("Cash Above Floor:", self.cash_gate_label)
        macro_layout.addRow("Rule 2 Final Decision:", self.rule2_final_label)
        
        layout.addWidget(macro_group)
        layout.addStretch()
    
    def save_macro_signals(self):
        self.main_window.settings["lei_signal"] = self.lei_input.value()
        self.main_window.settings["yield_curve_inverted"] = self.yield_curve_input.value()
        self.main_window.settings["sahm_rule_signal"] = self.sahm_input.value()
        self.main_window.save_settings()
        self.update_display()
    
    def update_display(self):
        prices = self.main_window.prices
        
        if "RSP" in prices:
            rsp_price = prices["RSP"]
            self.rsp_price_label.setText(f"${rsp_price:.2f}")
            
            rsp_yesterday = self.main_window.rsp_yesterday
            rsp_monthly_high = self.main_window.rsp_monthly_high
            
            if rsp_yesterday:
                self.rsp_yesterday_label.setText(f"${rsp_yesterday:.2f}")
                daily_change = (rsp_price / rsp_yesterday - 1) * 100
                self.rsp_daily_change_label.setText(f"{daily_change:+.2f}%")
            else:
                self.rsp_yesterday_label.setText("N/A")
                self.rsp_daily_change_label.setText("N/A")
            
            if rsp_monthly_high:
                self.rsp_monthly_high_label.setText(f"${rsp_monthly_high:.2f}")
                monthly_dd = (rsp_price / rsp_monthly_high - 1) * 100
                self.rsp_monthly_dd_label.setText(f"{monthly_dd:+.2f}%")
            else:
                self.rsp_monthly_high_label.setText("N/A")
                self.rsp_monthly_dd_label.setText("N/A")
            
            triggers = self.main_window.rules_engine.check_rule1_triggers(
                rsp_price, rsp_yesterday, rsp_monthly_high
            )
            
            self.buy1_label.setText("✅ Triggered" if triggers["buy1"] else "❌ No")
            self.buy2_label.setText("✅ Triggered" if triggers["buy2"] else "❌ No")
            self.buy3_label.setText("✅ Triggered" if triggers["buy3"] else "❌ No")
            self.fallback_label.setText("🟡 Window Open" if triggers["fallback"] else "")
        
        if "IWY" in prices and "SPMO" in prices:
            iwy_price = prices["IWY"]
            spmo_price = prices["SPMO"]
            iwy_40d = self.main_window.iwy_40d_ago
            spmo_40d = self.main_window.spmo_40d_ago
            
            self.iwy_price_label.setText(f"${iwy_price:.2f}")
            self.spmo_price_label.setText(f"${spmo_price:.2f}")
            
            if iwy_40d:
                self.iwy_40d_label.setText(f"${iwy_40d:.2f}")
            else:
                self.iwy_40d_label.setText("N/A")
            
            if spmo_40d:
                self.spmo_40d_label.setText(f"${spmo_40d:.2f}")
            else:
                self.spmo_40d_label.setText("N/A")
            
            triggered, iwy_ret, spmo_ret = self.main_window.rules_engine.check_rule2_trigger(
                iwy_price, iwy_40d, spmo_price, spmo_40d
            )
            
            if iwy_ret is not None:
                self.iwy_return_label.setText(f"{iwy_ret*100:+.2f}%")
            else:
                self.iwy_return_label.setText("N/A")
            
            if spmo_ret is not None:
                self.spmo_return_label.setText(f"{spmo_ret*100:+.2f}%")
            else:
                self.spmo_return_label.setText("N/A")
            
            self.price_trigger_label.setText("🟢 Triggered" if triggered else "🔴 No")
            
            macro_regime = self.main_window.rules_engine.check_macro_regime(
                self.main_window.settings["lei_signal"],
                self.main_window.settings["yield_curve_inverted"],
                self.main_window.settings["sahm_rule_signal"]
            )
            self.macro_regime_label.setText(macro_regime)
            
            cash_above_floor = self.main_window.rules_engine.check_cash_gate(
                self.main_window.target_cash_usd,
                self.main_window.floor_cash_usd
            )
            self.cash_gate_label.setText("✅ Yes" if cash_above_floor else "⛔ No")
            
            rule2_final = self.main_window.rules_engine.evaluate_rule2_final(
                triggered, macro_regime, cash_above_floor
            )
            self.rule2_final_label.setText(rule2_final)
