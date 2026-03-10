"""規則頁面 - 加執行按鈕"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                               QGroupBox, QSpinBox, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit, QComboBox)
from PySide6.QtCore import Qt

class RulesTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.custom_amount = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Rule 1 - DCA
        rule1_group = QGroupBox("Rule 1 - DCA Execution")
        rule1_layout = QVBoxLayout()
        rule1_group.setLayout(rule1_layout)
        
        rule1_form = QFormLayout()
        
        self.rsp_price_label = QLabel()
        self.rsp_yesterday_label = QLabel()
        self.rsp_daily_change_label = QLabel()
        self.rsp_monthly_high_label = QLabel()
        self.rsp_monthly_dd_label = QLabel()
        self.buy1_label = QLabel()
        self.buy2_label = QLabel()
        self.buy3_label = QLabel()
        self.fallback_label = QLabel()
        
        rule1_form.addRow("RSP Price:", self.rsp_price_label)
        rule1_form.addRow("RSP Yesterday:", self.rsp_yesterday_label)
        rule1_form.addRow("RSP Daily Change:", self.rsp_daily_change_label)
        rule1_form.addRow("RSP Monthly High:", self.rsp_monthly_high_label)
        rule1_form.addRow("RSP Monthly DD:", self.rsp_monthly_dd_label)
        rule1_form.addRow("Buy1 Trigger (>= -1.3%):", self.buy1_label)
        rule1_form.addRow("Buy2 Trigger (>= -5%):", self.buy2_label)
        rule1_form.addRow("Buy3 Trigger (>= -10%):", self.buy3_label)
        rule1_form.addRow("Fallback (3rd Friday):", self.fallback_label)
        
        rule1_layout.addLayout(rule1_form)
        
        # Investment Amount Input
        amount_group = QGroupBox("Investment Amount (USD)")
        amount_layout = QFormLayout()
        amount_group.setLayout(amount_layout)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount or leave empty for monthly minimum")
        self.amount_input.textChanged.connect(self.on_amount_changed)
        amount_layout.addRow("Total Investment:", self.amount_input)
        
        self.min_amount_label = QLabel()
        amount_layout.addRow("Min Required:", self.min_amount_label)
        
        self.monthly_min_label = QLabel()
        amount_layout.addRow("Monthly Minimum:", self.monthly_min_label)
        
        rule1_layout.addWidget(amount_group)
        
        # Rule 1 Execute Buttons
        rule1_btns = QHBoxLayout()
        self.buy1_btn = QPushButton("Execute Buy1")
        self.buy2_btn = QPushButton("Execute Buy2")
        self.buy3_btn = QPushButton("Execute Buy3")
        self.fallback_btn = QPushButton("Execute Fallback")
        
        self.buy1_btn.clicked.connect(lambda: self.execute_rule1('buy1'))
        self.buy2_btn.clicked.connect(lambda: self.execute_rule1('buy2'))
        self.buy3_btn.clicked.connect(lambda: self.execute_rule1('buy3'))
        self.fallback_btn.clicked.connect(lambda: self.execute_rule1('fallback'))
        
        rule1_btns.addWidget(self.buy1_btn)
        rule1_btns.addWidget(self.buy2_btn)
        rule1_btns.addWidget(self.buy3_btn)
        rule1_btns.addWidget(self.fallback_btn)
        rule1_layout.addLayout(rule1_btns)
        
        layout.addWidget(rule1_group)
        
        # Rule 1 Investment Table
        rule1_invest_group = QGroupBox("Investment Distribution")
        rule1_invest_layout = QVBoxLayout()
        rule1_invest_group.setLayout(rule1_invest_layout)
        
        self.rule1_table = QTableWidget()
        self.rule1_table.setColumnCount(5)
        self.rule1_table.setHorizontalHeaderLabels([
            "Ticker", "Weight", "Amount (USD)", "Shares", "Price (USD)"
        ])
        self.rule1_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rule1_table.setMaximumHeight(200)
        rule1_invest_layout.addWidget(self.rule1_table)
        
        layout.addWidget(rule1_invest_group)
        
        # Rule 2 - Tactical Overlay
        rule2_group = QGroupBox("🚀 Rule 2 - Tactical Overlay")
        rule2_layout = QVBoxLayout()
        rule2_group.setLayout(rule2_layout)
        
        rule2_form = QFormLayout()
        
        self.iwy_price_label = QLabel()
        self.iwy_40d_label = QLabel()
        self.iwy_return_label = QLabel()
        self.spmo_price_label = QLabel()
        self.spmo_40d_label = QLabel()
        self.spmo_return_label = QLabel()
        self.price_trigger_label = QLabel()
        
        rule2_form.addRow("IWY 目前價格:", self.iwy_price_label)
        rule2_form.addRow("IWY 40交易日前:", self.iwy_40d_label)
        rule2_form.addRow("IWY 40D 回報:", self.iwy_return_label)
        rule2_form.addRow("SPMO 目前價格:", self.spmo_price_label)
        rule2_form.addRow("SPMO 40交易日前:", self.spmo_40d_label)
        rule2_form.addRow("SPMO 40D 回報:", self.spmo_return_label)
        rule2_form.addRow("🎯 價格觸發 (both <= -20%):", self.price_trigger_label)
        
        self.rule2_sell_bnd_label = QLabel()
        self.rule2_buy_iwy_label = QLabel()
        self.rule2_buy_spmo_label = QLabel()
        
        rule2_form.addRow("Sell BND Amount:", self.rule2_sell_bnd_label)
        rule2_form.addRow("Buy IWY Amount:", self.rule2_buy_iwy_label)
        rule2_form.addRow("Buy SPMO Amount:", self.rule2_buy_spmo_label)
        
        rule2_layout.addLayout(rule2_form)
        
        # Rule 2 Execute Button
        self.rule2_btn = QPushButton("Execute Rule 2 Tactical")
        self.rule2_btn.setStyleSheet("padding: 10px; background-color: #FF5722; color: white; font-weight: bold;")
        self.rule2_btn.clicked.connect(self.execute_rule2)
        rule2_layout.addWidget(self.rule2_btn)
        
        layout.addWidget(rule2_group)
        
        # Macro Risk Gate
        macro_group = QGroupBox("Macro Economic Indicators & Regime")
        macro_layout = QFormLayout()
        macro_group.setLayout(macro_layout)
        
        self.yield_spread_label = QLabel()
        self.yield_curve_label = QLabel()
        
        # LEI Signal
        self.lei_input = QSpinBox()
        self.lei_input.setRange(0, 1)
        self.lei_input.setValue(self.main_window.settings.get("lei_signal", 0))
        macro_layout.addRow("LEI Recession Signal:", self.lei_input)
        macro_layout.addRow("  (0=Normal, 1=Active)", QLabel("YoY decline expanding"))
        
        # Yield Curve
        self.yield_input = QSpinBox()
        self.yield_input.setRange(0, 1)
        self.yield_input.setValue(self.main_window.settings.get("yield_curve_inverted", 0))
        macro_layout.addRow("10Y-3M < 0 (Inverted):", self.yield_input)
        
        # Sahm Rule
        self.sahm_input = QSpinBox()
        self.sahm_input.setRange(0, 100)
        self.sahm_input.setValue(int(self.main_window.settings.get("sahm_rule_signal", 0) * 100))
        self.sahm_input.setSuffix(" %")
        macro_layout.addRow("Sahm Rule (x100):", self.sahm_input)
        
        # CCI Expectations
        self.cci_input = QSpinBox()
        self.cci_input.setRange(0, 150)
        self.cci_input.setValue(self.main_window.settings.get("cci_signal", 0))
        macro_layout.addRow("CCI Expectations (<80):", self.cci_input)
        
        # Jobless Claims
        self.claims_input = QSpinBox()
        self.claims_input.setRange(0, 1000000)
        self.claims_input.setValue(self.main_window.settings.get("jobless_claims", 0))
        self.claims_input.setSuffix(" claims")
        macro_layout.addRow("Jobless Claims 4W MA:", self.claims_input)
        
        # Regime Override
        self.regime_combo = QComboBox()
        self.regime_combo.addItems(["Auto", "Trough (Manual)"])
        current_override = self.main_window.settings.get("regime_override", None)
        self.regime_combo.setCurrentText("Trough (Manual)" if current_override == "Trough" else "Auto")
        macro_layout.addRow("Regime Override:", self.regime_combo)
        
        save_macro_btn = QPushButton("Save Macro Signals")
        save_macro_btn.setStyleSheet("font-weight: bold; padding: 5px;")
        save_macro_btn.clicked.connect(self.save_macro_signals)
        macro_layout.addRow(save_macro_btn)
        
        # Economic Regime Display
        self.macro_regime_label = QLabel()
        self.macro_regime_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        macro_layout.addRow("Current Regime:", self.macro_regime_label)
        
        # Active Signals Count
        self.active_signals_label = QLabel()
        macro_layout.addRow("Active Signals:", self.active_signals_label)
        
        # Rules Status
        self.rules_status_label = QLabel()
        self.rules_status_label.setWordWrap(True)
        macro_layout.addRow("Rules Status:", self.rules_status_label)
        
        self.cash_gate_label = QLabel()
        macro_layout.addRow("Cash Above Floor:", self.cash_gate_label)
        
        self.rule2_final_label = QLabel()
        macro_layout.addRow("Rule 2 Decision:", self.rule2_final_label)
        
        layout.addWidget(macro_group)
        
        # AI Risk Flag Section
        ai_risk_group = QGroupBox("AI Risk Flag (Optional Gate)")
        ai_risk_layout = QFormLayout()
        ai_risk_group.setLayout(ai_risk_layout)
        
        self.ai_risk_enabled = QComboBox()
        self.ai_risk_enabled.addItems(["Disabled", "Enabled"])
        self.ai_risk_enabled.setCurrentText("Enabled" if self.main_window.settings.get("ai_risk_enabled") else "Disabled")
        ai_risk_layout.addRow("AI Risk Check:", self.ai_risk_enabled)
        
        self.qqq_months_input = QSpinBox()
        self.qqq_months_input.setRange(0, 12)
        self.qqq_months_input.setValue(self.main_window.settings.get("qqq_months_above_15pct", 0))
        ai_risk_layout.addRow("QQQ >15% DD (months):", self.qqq_months_input)
        
        self.vix_weeks_input = QSpinBox()
        self.vix_weeks_input.setRange(0, 52)
        self.vix_weeks_input.setValue(self.main_window.settings.get("vix_weeks_above_25", 0))
        ai_risk_layout.addRow("VIX >25 (weeks):", self.vix_weeks_input)
        
        self.ai_risk_status_label = QLabel()
        ai_risk_layout.addRow("AI Risk Status:", self.ai_risk_status_label)
        
        layout.addWidget(ai_risk_group)
        
        # Tactical Exit Signal Section
        tactical_exit_group = QGroupBox("Tactical Exit Signal")
        tactical_exit_layout = QFormLayout()
        tactical_exit_group.setLayout(tactical_exit_layout)
        
        self.tactical_exit_enabled = QComboBox()
        self.tactical_exit_enabled.addItems(["Disabled", "Enabled"])
        self.tactical_exit_enabled.setCurrentText("Enabled" if self.main_window.settings.get("tactical_exit_enabled") else "Disabled")
        tactical_exit_layout.addRow("Early Exit Check:", self.tactical_exit_enabled)
        
        self.tactical_exit_label = QLabel()
        self.tactical_exit_label.setWordWrap(True)
        tactical_exit_layout.addRow("Exit Signal:", self.tactical_exit_label)
        
        layout.addWidget(tactical_exit_group)
        
        layout.addStretch()
    
    def on_amount_changed(self):
        """Handle amount input change"""
        try:
            text = self.amount_input.text().strip()
            if text:
                self.custom_amount = float(text)
            else:
                self.custom_amount = None
        except ValueError:
            self.custom_amount = None
    
    def calculate_investments(self, amount):
        """Calculate investment distribution for given amount"""
        from core.config import TARGET_WEIGHTS
        
        prices = getattr(self.main_window, 'prices', {})
        investments = {}
        
        for ticker, weight in TARGET_WEIGHTS.items():
            if ticker in prices:
                ticker_amount = amount * weight
                shares = ticker_amount / prices[ticker]
                
                investments[ticker] = {
                    "amount_usd": ticker_amount,
                    "shares": shares,
                    "price": prices[ticker],
                    "weight": weight
                }
        
        return investments
    
    def execute_rule1(self, rule_type):
        """Execute Rule 1 buy"""
        # Determine amount to invest
        if self.custom_amount and self.custom_amount > 0:
            amount = self.custom_amount
            amount_text = f"${amount:,.2f}"
        else:
            amount = getattr(self.main_window, 'monthly_minimum', 0)
            amount_text = f"${amount:,.2f} (monthly minimum)"
        
        # Calculate investments
        investments = self.calculate_investments(amount)
        
        reply = QMessageBox.question(
            self,
            f"Confirm Rule 1 {rule_type.upper()}",
            f"Execute Rule 1 {rule_type.upper()} with {amount_text}?\n\nThis will invest in 6 ETFs proportionally.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.main_window.portfolio_manager.execute_rule1_buy(
                    investments,
                    self.main_window.prices,
                    rule_type
                )
                
                # Refresh data and update all tabs
                self.main_window.refresh_data()
                
                QMessageBox.information(
                    self,
                    "Execution Complete",
                    f"Rule 1 {rule_type.upper()} completed!\n\nAmount invested: {amount_text}\n\nAll portfolio metrics have been updated."
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Execution failed: {str(e)}")
    
    def execute_rule2(self):
        """Execute Rule 2 tactical"""
        reply = QMessageBox.question(
            self,
            "Confirm Rule 2 Tactical",
            "Execute Rule 2 Tactical Overlay?\n\nThis will sell 50% BND and buy IWY and SPMO.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.main_window.portfolio_manager.execute_rule2_tactical(
                    self.main_window.rule2_investments,
                    self.main_window.prices
                )
                
                # Refresh data and update all tabs
                self.main_window.refresh_data()
                
                QMessageBox.information(
                    self,
                    "Execution Complete",
                    "Rule 2 Tactical Overlay completed!\n\nAll portfolio metrics have been updated."
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Execution failed: {str(e)}")
    
    def save_macro_signals(self):
        self.main_window.settings["lei_signal"] = self.lei_input.value()
        self.main_window.settings["yield_curve_inverted"] = self.yield_input.value()
        self.main_window.settings["sahm_rule_signal"] = self.sahm_input.value() / 100.0
        self.main_window.settings["cci_signal"] = self.cci_input.value()
        self.main_window.settings["jobless_claims"] = self.claims_input.value()
        self.main_window.settings["regime_override"] = "Trough" if self.regime_combo.currentText() == "Trough (Manual)" else None
        # AI Risk Settings
        self.main_window.settings["ai_risk_enabled"] = self.ai_risk_enabled.currentText() == "Enabled"
        self.main_window.settings["qqq_months_above_15pct"] = self.qqq_months_input.value()
        self.main_window.settings["vix_weeks_above_25"] = self.vix_weeks_input.value()
        # Tactical Exit
        self.main_window.settings["tactical_exit_enabled"] = self.tactical_exit_enabled.currentText() == "Enabled"
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
            
            self.buy1_label.setText("Triggered" if triggers["buy1"] else "Not Triggered")
            self.buy2_label.setText("Triggered" if triggers["buy2"] else "Not Triggered")
            self.buy3_label.setText("Triggered" if triggers["buy3"] else "Not Triggered")
            self.fallback_label.setText("Window Open" if triggers["fallback"] else "")
        
        # Update min amount and monthly minimum
        if hasattr(self.main_window, 'monthly_minimum'):
            self.monthly_min_label.setText(f"${self.main_window.monthly_minimum:,.2f}")
        
        # Calculate minimum required (based on cheapest ETF price)
        from core.config import TARGET_WEIGHTS
        prices = getattr(self.main_window, 'prices', {})
        if prices:
            min_required = float('inf')
            for ticker, weight in TARGET_WEIGHTS.items():
                if ticker in prices and prices[ticker] > 0:
                    # Minimum for 1 share at target weight
                    min_for_one_share = prices[ticker] / weight
                    min_required = min(min_required, min_for_one_share)
            if min_required != float('inf'):
                self.min_amount_label.setText(f"${min_required:,.2f} (approx)")
            else:
                self.min_amount_label.setText("N/A")
        
        # Rule 1 Investment Table - use custom amount if set, otherwise monthly minimum
        amount = self.custom_amount if self.custom_amount else getattr(self.main_window, 'monthly_minimum', 0)
        if amount > 0 and prices:
            investments = self.calculate_investments(amount)
        elif hasattr(self.main_window, 'rule1_investments'):
            investments = self.main_window.rule1_investments
        else:
            investments = {}
        
        self.rule1_table.setRowCount(len(investments))
        
        row = 0
        for ticker, data in sorted(investments.items()):
            self.rule1_table.setItem(row, 0, QTableWidgetItem(ticker))
            self.rule1_table.setItem(row, 1, QTableWidgetItem(f"{data.get('weight', 0)*100:.0f}%"))
            self.rule1_table.setItem(row, 2, QTableWidgetItem(f"${data['amount_usd']:.2f}"))
            self.rule1_table.setItem(row, 3, QTableWidgetItem(f"{data['shares']:.2f}"))
            self.rule1_table.setItem(row, 4, QTableWidgetItem(f"${data['price']:.2f}"))
            row += 1
        
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
            
            self.price_trigger_label.setText("Triggered" if triggered else "Not Triggered")
            
            # Rule 2 Investment Display
            if hasattr(self.main_window, 'rule2_investments'):
                r2_inv = self.main_window.rule2_investments
                self.rule2_sell_bnd_label.setText(f"${r2_inv.get('sell_bnd_amount', 0):.2f}")
                self.rule2_buy_iwy_label.setText(f"${r2_inv.get('iwy_buy_amount', 0):.2f} ({r2_inv.get('iwy_shares', 0):.2f} shares)")
                self.rule2_buy_spmo_label.setText(f"${r2_inv.get('spmo_buy_amount', 0):.2f} ({r2_inv.get('spmo_shares', 0):.2f} shares)")
            
            # Macro Display
            yield_spread = getattr(self.main_window, 'yield_spread', None)
            if yield_spread is not None:
                self.yield_spread_label.setText(f"{yield_spread:.2f}%")
            else:
                self.yield_spread_label.setText("N/A")
            
            # Get macro regime using new function
            macro_regime = self.main_window.rules_engine.check_macro_regime(
                self.main_window.settings,
                yield_spread
            )
            
            # Get indicators
            indicators = self.main_window.rules_engine.macro_indicators
            active_count = sum(1 for ind in indicators if ind.is_active)
            
            regime_colors = {
                "Expansion": "Green - Expansion",
                "Peak": "Yellow - Peak",
                "Contraction": "Red - Contraction/Recession",
                "Trough": "Blue - Trough"
            }
            self.macro_regime_label.setText(regime_colors.get(macro_regime, macro_regime))
            
            self.active_signals_label.setText(f"{active_count}/5 signals active")
            
            # Show rules status
            rules = self.main_window.rules_engine.get_regime_rules(macro_regime)
            rules_text = f"Rule1 DCA: {rules['rule1_dca']}\nRule2 Tactical: {rules['rule2_tactical']}\nExtra Buys: {rules['extra_buys']}"
            self.rules_status_label.setText(rules_text)
            
            cash_above_floor = self.main_window.rules_engine.check_cash_gate(
                self.main_window.target_cash_usd,
                self.main_window.floor_cash_usd
            )
            self.cash_gate_label.setText("Yes" if cash_above_floor else "No")
            
            # AI Risk Check
            ai_risk = self.main_window.rules_engine.check_ai_risk(self.main_window.settings)
            if ai_risk["enabled"]:
                if ai_risk["is_active"]:
                    self.ai_risk_status_label.setText(f"ACTIVE - {ai_risk.get('reason', '')}")
                    self.ai_risk_status_label.setStyleSheet("color: red; font-weight: bold;")
                else:
                    self.ai_risk_status_label.setText("Normal - No AI risk detected")
                    self.ai_risk_status_label.setStyleSheet("color: green;")
            else:
                self.ai_risk_status_label.setText("Disabled")
                self.ai_risk_status_label.setStyleSheet("color: gray;")
            
            # Tactical Exit Signal Check
            rsp_current = prices.get("RSP")
            rsp_40d = getattr(self.main_window, 'rsp_yesterday', None)
            iwy_current = prices.get("IWY")
            iwy_40d = getattr(self.main_window, 'iwy_40d_ago', None)
            spmo_current = prices.get("SPMO")
            spmo_40d = getattr(self.main_window, 'spmo_40d_ago', None)
            
            if self.main_window.settings.get("tactical_exit_enabled") and all([rsp_current, rsp_40d, iwy_current, iwy_40d, spmo_current, spmo_40d]):
                exit_signal = self.main_window.rules_engine.check_tactical_exit_signal(
                    rsp_current, rsp_40d, iwy_current, iwy_40d, spmo_current, spmo_40d
                )
                if exit_signal["should_exit"]:
                    self.tactical_exit_label.setText(f"EXIT SIGNAL - {exit_signal['reason']} (Exit {exit_signal['exit_percentage']}%)")
                    self.tactical_exit_label.setStyleSheet("color: orange; font-weight: bold;")
                else:
                    self.tactical_exit_label.setText("No exit signal - RSP vs tactical performance within normal range")
                    self.tactical_exit_label.setStyleSheet("color: green;")
            else:
                self.tactical_exit_label.setText("Disabled or insufficient data")
                self.tactical_exit_label.setStyleSheet("color: gray;")
            
            # Final Rule 2 Decision
            rule2_final = self.main_window.rules_engine.evaluate_rule2_final(
                triggered, macro_regime, cash_above_floor, ai_risk
            )
            
            final_display = {
                "Execute": "Execute",
                "No Trigger": "No Trigger",
                "Paused (Peak)": "Paused (Peak)",
                "Paused (Contraction)": "Paused (Contraction)",
                "Paused (Trough)": "Paused (Trough)",
                "Blocked by Cash": "Blocked by Cash"
            }
            if "AI Risk Active" in rule2_final:
                self.rule2_final_label.setText(rule2_final)
                self.rule2_final_label.setStyleSheet("color: red;")
            else:
                self.rule2_final_label.setText(final_display.get(rule2_final, rule2_final))
                self.rule2_final_label.setStyleSheet("")
