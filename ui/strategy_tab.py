"""策略規則頁面"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel)
from PySide6.QtCore import Qt

class StrategyTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Hi5 投資策略 (Investment Strategy)")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        rules_text = QTextEdit()
        rules_text.setReadOnly(True)
        rules_text.setStyleSheet("font-size: 12px; line-height: 1.5;")
        
        rules_content = """
=== 組合配置 (Portfolio Allocation) ===
IWY 20% | SPMO 20% | RSP 20% | PFF 20% | BND 10% | BNDW 10%

=== 現金政策 (Cash Policy) ===
• 目標現金 = 12 x 每月最低投資額
• 現金底線 = 9 x 最低 (低於暫停 Tactical)
• 現金上限 = 18 x 最低 (可考慮額外買入)

=== 投資模式 (Investment Modes) ===
Working Mode: 每月最低 = 1000 USD + TTM股息/12
Student Mode: 每月最低 = TTM股息/12 (最少 100 USD)

=== Rule 1 - DCA 規則（加強版：加 volume + MA 確認） ===
觸發條件:
• Buy1: RSP 單日跌 >= -1.3% **AND** 當日成交量 > 20日平均成交量
• Buy2: RSP 月內回撤 >= -5% **AND** RSP 現價 < 50日 MA
• Buy3: RSP 月內回撤 >= -10% **AND** (當日成交量 > 50日平均成交量 **OR** RSP 現價 < 200日 MA)
• Fallback: 月內無觸發，第3個星期五執行（若當日 RSP < 50日 MA，可加碼 20%）
• 每月最多 3    次買入

金額分配: 按目標權重分配到 6 隻 ETF  
（可選：若 RSP 跌穿 50日 MA 超過 10%，臨時 overweight RSP 5–10%）

濾波 override: 若 trigger 響但 volume/MA 唔達標，記為「missed signal」，次日再 check 若改善可用 50% 份額執行

=== Rule 2 - Tactical Overlay（加強版：加 volume + MA 確認） ===
觸發條件:
• IWY 同 SPMO 較 40 日前跌 >= 20% **AND** (過去 40 日平均成交量 > 50日歷史平均 **OR** 兩隻現價 < 50日 MA)

操作:
• 賣出 50% BND
• 買入 50% IWY + 50% SPMO（建議分段：先買 25%，若再跌 5% 或 volume 爆 >2x 20日平均，再補剩餘）

限制:
• 3 個月內不能重複觸發
• 現金必須高於底線
• 宏觀 regime 必須係 Expansion
• 若 volume 低過平均，等多最多 5 個交易日每日 re-check 確認

=== 新 Rule 3 - Volume Spike Booster（爆量加碼） ===
觸發條件:
• 任何 Rule 1 或 Rule 2 買入日，該 ETF 成交量 > 2x 20日平均成交量（capitulation 信號）

操作:
• 買入金額加 20–30%（現金夠就加，唔夠減低個月 DCA）

限制:
• 每月只限一次
• 宏觀唔可以係 Contraction

=== 新 Rule 4 - MA Crossover 輔助信號 ===
觸發條件:
• 買入後：RSP 由下向上穿 50日 MA → 可再加 10% 買入（確認反彈）
• Tactical 持有中：IWY/SPMO 跌穿 200日 MA → 考慮 partial exit 20%（防長熊）

整合 Tactical Exit:
• 若 RSP 表現跑贏 IWY/SPMO 超過 10% (40 日) **AND** RSP > 50日 MA → 建議加快賣出 30–50% tactical position

=== 宏觀經濟週期 (Macro Regime) ===
5 個指標:
1. LEI Recession Signal: 年比跌幅擴大
2. 10Y-3M Yield Spread: < 0 (倒掛)
3. Sahm Rule: >= 0.50
4. CCI Expectations: < 80
5. Jobless Claims 4W MA: > 400,000

判斷:
🟢 Expansion (0 個 signal): 所有規則正常
🟡 Peak (1-2 signals): Rule 1 正常，Rule 2 暫停
🔴 Contraction (3+ signals): 只做最低 DCA，Rule 2 & Rule 3 暫停
🔵 Trough: 手動判斷

=== AI Risk Flag (Optional) ===
保護 Tactical Overlay 免受 AI/泡沫調整影響

條件:
1. QQQ 回撤 >= 15% 持續 2 個月
2. 或 VIX > 25 持續 2 週

如果 AI Risk Active:
→ 暫停 Tactical Overlay (即使 macro 係 Peak/Expansion)

=== Tactical Exit 彈性 ===
如果 RSP 表現跑贏 IWY/SPMO 超過 10% (40 日)  
→ 建議賣出 30-50% tactical position  
（若 RSP > 50日 MA 更強烈建議執行）

作用: 捕捉 AI/增長 → 實體經濟 嘅輪動

=== Annual Rebalance ===
每年 8 月檢查權重
偏離 > ±2% 就 rebalance
Tactical 倉位會自動拉回目標權重

=== 執行原則 ===
除非有完整 backtest + 起碼 2 年實盤證據，
否則唔改核心規則。
特別注意：volume + MA 濾波屬「加強層」，backtest 後若明顯降低交易次數或表現變差，可調鬆條件（例如 volume 改 1.5x、MA 改 20日等）。
"""
        
        rules_text.setPlainText(rules_content)
        layout.addWidget(rules_text)
