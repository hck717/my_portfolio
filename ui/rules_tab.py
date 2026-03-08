"""規則頁面"""
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
        
        # Rule 1 - DCA
        rule1_group = QGroupBox("⚙️ Rule 1 - DCA 觸發判斷")
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
        
        rule1_layout.addRow("RSP 目前價格:", self.rsp_price_label)
        rule1_layout.addRow("RSP 昨日收市:", self.rsp_yesterday_label)
        rule1_layout.addRow("RSP 單日變化:", self.rsp_daily_change_label)
        rule1_layout.addRow("RSP 月內高位:", self.rsp_monthly_high_label)
        rule1_layout.addRow("RSP 月內回撤:", self.rsp_monthly_dd_label)
        rule1_layout.addRow("🟢 Buy1 觸發 (>= -1%):", self.buy1_label)
        rule1_layout.addRow("🟡 Buy2 觸發 (>= -5%):", self.buy2_label)
        rule1_layout.addRow("🔴 Buy3 觸發 (>= -10%):", self.buy3_label)
        rule1_layout.addRow("🟡 第3個星期五保底:", self.fallback_label)
        
        layout.addWidget(rule1_group)
        
        # Rule 2 - Tactical Overlay
        rule2_group = QGroupBox("🚀 Rule 2 - Tactical Overlay")
        rule2_layout = QFormLayout()
        rule2_group.setLayout(rule2_layout)
        
        self.iwy_price_label = QLabel()
        self.iwy_40d_label = QLabel()
        self.iwy_return_label = QLabel()
        self.spmo_price_label = QLabel()
        self.spmo_40d_label = QLabel()
        self.spmo_return_label = QLabel()
        self.price_trigger_label = QLabel()
        
        rule2_layout.addRow("IWY 目前價格:", self.iwy_price_label)
        rule2_layout.addRow("IWY 40交易日前:", self.iwy_40d_label)
        rule2_layout.addRow("IWY 40D 回報:", self.iwy_return_label)
        rule2_layout.addRow("SPMO 目前價格:", self.spmo_price_label)
        rule2_layout.addRow("SPMO 40交易日前:", self.spmo_40d_label)
        rule2_layout.addRow("SPMO 40D 回報:", self.spmo_return_label)
        rule2_layout.addRow("🎯 價格觸發 (both <= -20%):", self.price_trigger_label)
        
        layout.addWidget(rule2_group)
        
        # Macro Risk Gate
        macro_group = QGroupBox("🌍 宏觀風險閘門")
        macro_layout = QFormLayout()
        macro_group.setLayout(macro_layout)
        
        self.yield_spread_label = QLabel()
        self.yield_curve_label = QLabel()
        
        self.lei_input = QSpinBox()
        self.lei_input.setRange(0, 1)
        self.lei_input.setValue(self.main_window.settings.get("lei_signal", 0))
        
        self.sahm_input = QSpinBox()
        self.sahm_input.setRange(0, 1)
        self.sahm_input.setValue(self.main_window.settings.get("sahm_rule_signal", 0))
        
        macro_layout.addRow("📊 10Y-3M Spread:", self.yield_spread_label)
        macro_layout.addRow("⚠️ 10Y-3M 倒掛 (0/1):", self.yield_curve_label)
        macro_layout.addRow("🚨 LEI Signal (0/1) [手動]:", self.lei_input)
        macro_layout.addRow("🔴 Sahm Rule (0/1) [手動]:", self.sahm_input)
        
        save_macro_btn = QPushButton("✅ 儲存宏觀訊號")
        save_macro_btn.clicked.connect(self.save_macro_signals)
        macro_layout.addRow(save_macro_btn)
        
        self.macro_regime_label = QLabel()
        self.cash_gate_label = QLabel()
        self.rule2_final_label = QLabel()
        
        macro_layout.addRow("🎯 宏觀狀態:", self.macro_regime_label)
        macro_layout.addRow("💰 現金高於底線:", self.cash_gate_label)
        macro_layout.addRow("✅ Rule 2 最終決定:", self.rule2_final_label)
        
        layout.addWidget(macro_group)
        layout.addStretch()
    
    def save_macro_signals(self):
        self.main_window.settings["lei_signal"] = self.lei_input.value()
        self.main_window.settings["sahm_rule_signal"] = self.sahm_input.value()
        self.main_window.save_settings()
        self.update_display()
    
    def update_display(self):
        prices = self.main_window.prices
        
        # Rule 1 Display
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
            
            self.buy1_label.setText("✅ 已觸發" if triggers["buy1"] else "❌ 未觸發")
            self.buy2_label.setText("✅ 已觸發" if triggers["buy2"] else "❌ 未觸發")
            self.buy3_label.setText("✅ 已觸發" if triggers["buy3"] else "❌ 未觸發")
            self.fallback_label.setText("🟡 窗口開啟" if triggers["fallback"] else "")
        
        # Rule 2 Display
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
            
            self.price_trigger_label.setText("🟢 已觸發" if triggered else "🔴 未觸發")
            
            # Macro Display
            if hasattr(self.main_window, 'yield_spread') and self.main_window.yield_spread is not None:
                self.yield_spread_label.setText(f"{self.main_window.yield_spread:.2f}%")
            else:
                self.yield_spread_label.setText("N/A")
            
            yield_inverted = self.main_window.settings.get('yield_curve_inverted', 0)
            self.yield_curve_label.setText("⚠️ 已倒掛" if yield_inverted == 1 else "✅ 正常")
            
            macro_regime = self.main_window.rules_engine.check_macro_regime(
                self.main_window.settings.get("lei_signal", 0),
                yield_inverted,
                self.main_window.settings.get("sahm_rule_signal", 0)
            )
            
            regime_colors = {
                "Normal": "🟢 Normal",
                "Caution": "🟡 Caution",
                "Recession": "🔴 Recession"
            }
            self.macro_regime_label.setText(regime_colors.get(macro_regime, macro_regime))
            
            cash_above_floor = self.main_window.rules_engine.check_cash_gate(
                self.main_window.target_cash_usd,
                self.main_window.floor_cash_usd
            )
            self.cash_gate_label.setText("✅ 是" if cash_above_floor else "⛔ 否")
            
            rule2_final = self.main_window.rules_engine.evaluate_rule2_final(
                triggered, macro_regime, cash_above_floor
            )
            
            final_display = {
                "Execute": "✅ 可執行",
                "No Trigger": "❌ 未觸發",
                "Blocked by Macro": "⚠️ 被宏觀阻擋",
                "Blocked by Cash": "⚠️ 被現金阻擋"
            }
            self.rule2_final_label.setText(final_display.get(rule2_final, rule2_final))
