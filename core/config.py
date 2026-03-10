"""Configuration and constants"""

# ETF Tickers
TICKERS = ["IWY", "SPMO", "RSP", "PFF", "BND", "BNDW"]

# Target Weights
TARGET_WEIGHTS = {
    "IWY": 0.20,
    "SPMO": 0.20,
    "RSP": 0.20,
    "PFF": 0.20,
    "BND": 0.10,
    "BNDW": 0.10
}

# ETF Roles
ETF_ROLES = {
    "IWY": "Alpha (Top 200 Growth)",
    "SPMO": "Alpha (S&P 500 Momentum)",
    "RSP": "Beta (S&P 500 Equal Weight)",
    "PFF": "Income (Preferred Stock)",
    "BND": "Defensive (US Bonds)",
    "BNDW": "Defensive (Global Bonds)"
}

# Default Settings
DEFAULT_SETTINGS = {
    "current_assets_hkd": 400000,
    "mode": "working",
    "extra_investable_usd": 0,
    "fx_rate": 7.8,
    # Core Macro Indicators
    "lei_signal": 0,                    # LEI recession signal (0/1)
    "yield_curve_inverted": 0,          # 10Y-3M spread < 0 (0/1)
    "sahm_rule_signal": 0,             # Sahm rule >= 0.50
    "cci_signal": 0,                    # CCI Expectations Index (< 80)
    "jobless_claims": 0,                # Initial Jobless Claims 4W MA (> 400000)
    "regime_override": None,            # Manual override: "Trough"
    # AI Risk Flag (Optional additional gate)
    "ai_risk_enabled": False,          # Enable/disable AI risk check
    "qqq_current": None,               # QQQ current price
    "qqq_monthly_high": None,          # QQQ monthly high
    "qqq_months_above_15pct": 0,       # Months with >15% drawdown
    "vix_current": None,                # Current VIX level
    "vix_weeks_above_25": 0,           # Weeks with VIX > 25
    # Tactical Exit Signal
    "tactical_exit_enabled": True,     # Enable early exit signal
}

# Working Mode
WORKING_MODE_BASE = 1000  # USD

# Tactical Rules
TACTICAL_LOOKBACK_DAYS = 40
TACTICAL_DROP_THRESHOLD = -0.20
TACTICAL_BND_SELL_PCT = 0.50

# Rule 1 Thresholds
RULE1_BUY1_THRESHOLD = -0.013  # -1.3%
RULE1_BUY2_THRESHOLD = -0.05   # -5%
RULE1_BUY3_THRESHOLD = -0.10   # -10%

# Rebalance
REBALANCE_MONTH = 8
REBALANCE_DEVIATION_BAND = 0.02
