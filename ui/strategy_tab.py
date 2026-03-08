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
        
        title = QLabel("📋 Hi5 投資策略完整規則")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        rules_text = QTextEdit()
        rules_text.setReadOnly(True)
        rules_text.setStyleSheet("font-size: 13px; line-height: 1.6;")
        
        rules_content = """
🎯 核心一頁宣言
「核心配置 + 規則DCA + Tactical Overlay + Macro Risk Gate + 8月再平衡 + 10年不改核心框架」

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 新版配置
IWY 20% | SPMO 20% | RSP 20% | PFF 20% | BND 10% | BNDW 10%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 現金持有政策
• 現金持有目標 = 12 × 每月最低投資額
• 現金戶口只用作 DCA 與 emergency reserve
• 若現金低於 9 個月最低投資額，暫停 tactical overlays
• 若現金高於 18 個月最低投資額，可考慮額外一次性補倉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💼 Working Mode
每月最低投資額 = 1000 USD + 過去 12 個月實收股息 / 12

🎓 Student Mode
每月最低投資額 = 過去 12 個月實收股息 / 12（最少 100 USD）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️ Rule 1 - DCA 規則

第1次買入觸發條件：
• RSP 單日跌幅 <= -1% 即觸發
• 若全月未觸發，則於當月第 3 個星期五保底買入

第2次買入觸發條件：
• 若 RSP 從當月高點回撤 >= -5%，觸發第 2 次買入

第3次買入觸發條件：
• 若 RSP 從當月高點回撤 >= -10%，觸發第 3 次買入
• 每月最多 3 次

資金分配：
每次買入金額按 Working Mode 每月最低投資額執行，並按戰略權重分配至 6 隻 ETF：
IWY 20%、SPMO 20%、RSP 20%、PFF 20%、BND 10%、BNDW 10%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Rule 2 - Tactical Overlay

觸發條件（Trigger）：
• 若 IWY 與 SPMO 都較 40 個交易日前「收市價」下跌至少 20%

操作（Action）：
• 賣出 50% 的 BND
• 所得資金 50% 買入 IWY、50% 買入 SPMO

限制（Limits）：
• 每次觸發後 3 個月內不得重複觸發
• 若現金低於 9 個月最低投資額，暫停 Rule 2
• 若宏觀狀態非 Expansion，暫停 Rule 2

退出（Exit）：
• Tactical 倉位不設獨立止賺
• 持有至下一次年度 8 月再平衡時，由再平衡自動拉回戰略權重

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌍 Macro Overlay Rule

宏觀週期只作風險閘門，不取代 Rule 1。
每月檢查 3 個指標：
• Conference Board LEI recession signal
• 10Y-3M yield spread 是否低於 0
• Sahm Rule 是否 >= 0.50

經濟週期判斷：
🟢 Expansion（擴張期）
   0 個 signals active：所有規則照常執行

🟡 Peak（高峰期）
   1 個 signal active：Rule 1 照常，但暫停 Rule 2 tactical overlay

🔴 Contraction/Recession（收縮/衰退期）
   2 個或以上 signals active：只保留 Rule 1 最低 DCA，暫停 Rule 2 tactical overlay

🔵 Trough（谷底期）
   需手動判斷，當經濟指標開始改善但仍在低位時

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚖️ Annual Rebalance

• 每年 8 月初檢查權重
• 若偏離目標超過 ±2%，則再平衡回目標配置
• Tactical 倉位會在此時自動拉回戰略權重

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 組合哲學

目標係長期風險調整後回報，而唔係每段時間都跑贏 SPY。
若 Sharpe 較高、Beta 較低、Max Drawdown 較細，即使 CAGR 略低亦可接受。

🧠 執行原則

除非有完整 backtest + 至少 2 年實盤證據，否則不得更改核心規則。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        rules_text.setPlainText(rules_content)
        layout.addWidget(rules_text)
