"""
Constants and thresholds for analysis rules
"""

# Decision outcomes
DECISION_ACCUMULATE = "✅ Long-term Accumulate"
DECISION_AVOID = "⚠️ Avoid fresh buying at current levels"
DECISION_EXIT = "❌ Exit thesis broken"

# Fundamental Analysis Thresholds - IMPROVED FOR LESS CONSERVATIVE APPROACH
FUNDAMENTAL_THRESHOLDS = {
    # Profitability metrics
    "min_profit_margin_pct": 3.0,  # ← LOWERED from 5.0 (allow some weaker businesses)
    "min_roe_pct": 8.0,  # ← LOWERED from 10.0 (PSUs have lower ROE)
    "min_roce_pct": 10.0,  # ← LOWERED from 12.0 (allows more stocks)
    
    # Growth metrics - IMPORTANT: Still require growth
    "min_revenue_growth_5yr_pct": 6.0,  # ← LOWERED from 8.0 (modest growth OK)
    "min_eps_growth_5yr_pct": 6.0,  # ← LOWERED from 8.0 (modest growth OK)
    
    # Stability metrics - RELAXED FOR PSUs
    "max_debt_to_equity": 2.0,  # ← RAISED from 1.5 (PSUs have leverage)
    "min_current_ratio": 0.8,  # ← LOWERED from 1.0 (PSU constraint)
    "min_debt_service_coverage": 1.2,  # ← LOWERED from 1.5 (PSU reality)
    
    # Valuation (relative to history/sector) - More relaxed
    "max_pe_ratio_percentile": 85,  # ← RAISED from 75 (allow higher in growth)
    "max_pb_ratio": 4.0,  # ← RAISED from 3.0 (allow premium stocks)
    "min_dividend_yield_pct": 0.5,  # ← LOWERED from 1.5 (not all have dividends)
}

# Technical Analysis Thresholds - IMPROVED FOR RECOVERY STOCK DETECTION
TECHNICAL_THRESHOLDS = {
    # Trend confirmation
    "sma_short_period": 20,  # 20-day SMA
    "sma_long_period": 200,  # 200-day SMA
    
    # Momentum - LOWERED thresholds
    "rsi_period": 14,
    "rsi_oversold": 25,  # ← LOWERED from 30 (allow more oversold bounces)
    "rsi_overbought": 75,  # ← LOWERED from 70 (give uptrends room)
    "rsi_neutral_low": 40,  # ← NEW: RSI below this = weak
    "rsi_neutral_high": 60,  # ← NEW: RSI above this = strong
    
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    
    # Volatility
    "atr_period": 14,
    
    # Volume confirmation - More flexible
    "min_volume_ma_period": 20,
    "volume_surge_multiplier": 1.2,  # ← LOWERED from 1.5 (easier confirmation)
    
    # Entry thresholds by stock type (DYNAMIC)
    "entry_thresholds": {
        'blue_chip': {'fund': 65, 'tech': 65},
        'psu_government': {'fund': 55, 'tech': 60},
        'recovery_turnaround': {'fund': 50, 'tech': 65, 'momentum': 65},
        'cyclical_volatile': {'fund': 60, 'tech': 70}
    },
}

# Risk Assessment
RISK_PARAMETERS = {
    "max_single_stock_allocation": 5.0,  # Max % per stock
    "max_sector_allocation": 25.0,  # Max % per sector
    
    # Stop-loss rules (from entry)
    "strict_stop_loss_pct": 10.0,  # Hard stop below entry - 10%
    "technical_stop_loss_pct": 15.0,  # Below trend support - 15%
    
    # Target allocation periods
    "minimum_holding_period_years": 3,
    "target_horizon_years": 5,
}

# Data Quality Requirements
DATA_REQUIREMENTS = {
    "min_trading_days_history": 250,  # ~1 year of daily data
    "min_quarterly_reports": 4,  # At least 1 year of fundamentals
    "min_annual_reports": 2,  # At least 2 years
}

# Sector Classifications (NSE)
NSE_SECTORS = {
    "IT": ["TCS", "INFY", "WIPRO", "TECHM", "HCLTECH"],
    "BANKING": ["HDFC", "ICICIBANK", "AXIS", "KOTAK", "SBIN"],
    "PHARMA": ["SUNPHARMA", "CIPLA", "LUPIN", "DIVI", "AUROPHA"],
    "FMCG": ["HUL", "NESTLEIND", "BRITANNIA", "DABUR", "COLPAL"],
    "CAPITAL_GOODS": ["BHEL", "SIEMENS", "ABB", "RITES"],
    "AUTO": ["MARUTI", "HEROMOTOCO", "BAJAJFINSV", "TVS", "EICHER"],
    "METALS": ["TATASTEEL", "JSW", "HINDALCO", "TATA", "VEDL"],
    "POWER": ["NTPC", "THERMAL", "INDIGO", "TORRENTPHAR"],
    "REAL_ESTATE": ["DLF", "UNITECH", "OBEROI", "PURAVANKARA"],
}

# Stock-Type-Specific Thresholds (IMPROVED SYSTEM)
STOCK_TYPE_THRESHOLDS = {
    'blue_chip': {
        'fund_min': 65,
        'tech_min': 65,
        'example': 'TCS, INFY, HDFCBANK',
        'characteristics': 'Low leverage, stable growth, high quality'
    },
    'psu_government': {
        'fund_min': 55,
        'tech_min': 60,
        'max_debt_to_equity': 2.0,
        'example': 'HUDCO, NTPC, POWERGRID',
        'characteristics': 'Higher leverage OK (government-backed), dividends strong'
    },
    'recovery': {
        'fund_min': 45,
        'tech_min': 65,
        'momentum_min': 65,
        'example': 'HCC, distressed turnarounds',
        'characteristics': 'Momentum + tech strong, fundamentals improving'
    },
    'cyclical': {
        'fund_min': 60,
        'tech_min': 55,
        'volatility_adjusted': True,
        'example': 'VEDL, TATA, mining stocks',
        'characteristics': 'High volatility, but uptrend in commodities'
    }
}

