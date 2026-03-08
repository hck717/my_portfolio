# Hi5 Portfolio Desktop App

本地桌面投資組合管理工具，用於管理 Hi5 ETF 策略。

## 功能

- 自動抓取 ETF 即時價格與股息資料
- 計算每月最低投資額（Working / Student 模式）
- 現金持有政策自動計算（12x / 9x / 18x 月最低額）
- ETF 配置自動分配（IWY / SPMO / RSP / PFF / BND / BNDW）
- Rule 1 DCA 觸發判斷
- Rule 2 Tactical Overlay 判斷
- Macro Regime 風險閘門

## 安裝

```bash
pip install -r requirements.txt
```

## 使用

```bash
python app.py
```

## 架構

- `core/`: 核心邏輯（配置、資料服務、投資組合引擎、規則引擎）
- `ui/`: PySide6 GUI 介面
- `data/`: 本地設定檔

## 輸入參數

只需輸入 3 樣：
1. Current Assets (HKD)
2. Mode (working / student)
3. Extra Investable Amount Above Minimum (USD)

其餘全部自動計算。

## ETF 配置

- IWY: 20% (Alpha - Top 200 Growth)
- SPMO: 20% (Alpha - S&P 500 Momentum)
- RSP: 20% (Beta - S&P 500 Equal Weight)
- PFF: 20% (Income - Preferred Stock)
- BND: 10% (Defensive - US Bonds)
- BNDW: 10% (Defensive - Global Bonds)

## 現金政策

- 目標現金 = 12 × 每月最低投資額
- 現金底線 = 9 × 每月最低投資額（低於此暫停 tactical overlay）
- 現金上限 = 18 × 每月最低投資額（高於此可考慮額外補倉）

## 規則

### Rule 1 - DCA
- Buy1: RSP 單日跌 >= 1%
- Buy2: RSP 月內回撤 >= 5%
- Buy3: RSP 月內回撤 >= 10%
- Fallback: 每月第3個星期五保底買入

### Rule 2 - Tactical Overlay
- 觸發: IWY 與 SPMO 同時較 40 交易日前跌 >= 20%
- 操作: 賣 50% BND，50% 買 IWY + 50% 買 SPMO
- 限制: 3 個月 cooldown，需現金高於底線，需 Normal macro regime
- 退出: 持有至下次 8 月再平衡

### Macro Risk Gate
- Normal (0 signals): 所有規則照常
- Caution (1 signal): 暫停 Rule 2
- Recession (2+ signals): 只保留 Rule 1 最低 DCA

Signals: LEI recession / 10Y-3M inverted / Sahm Rule >= 0.50
