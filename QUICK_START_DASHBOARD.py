#!/usr/bin/env python3
"""
QUICK START GUIDE FOR NIFTY50 DASHBOARD
Copy-paste commands below to run the dashboard
"""

# ============================================================================
# STEP 1: Install Streamlit (one-time only)
# ============================================================================
# Open PowerShell and run:
# pip install streamlit

# ============================================================================
# STEP 2: Run the Dashboard
# ============================================================================
# Copy this command and run in PowerShell:

# cd C:\PythonProjects\ShareMarketBot ; streamlit run dashboard.py

# That's it! 🎉

# ============================================================================
# WHAT YOU'LL SEE
# ============================================================================
# 1. A beautiful dashboard opens in your browser (http://localhost:8501)
# 2. Shows NIFTY50 trading recommendations for today
# 3. Three sections: BUY (green), HOLD (orange), SELL (red)
# 4. All stocks with prices, targets, stop losses, and confidence levels
# 5. Auto-loads today's data or generates it if missing

# ============================================================================
# KEY FEATURES
# ============================================================================
# ✅ Checks if today's JSON file exists
# ✅ Auto-generates data if file not available (runs nifty50_weekly_automation.py)
# ✅ Beautiful, professional UI with gradients and colors
# ✅ Responsive tables with all recommendation details
# ✅ No backend changes - frontend only!

# ============================================================================
# FULL COMMAND (Copy & Paste)
# ============================================================================
"""
cd C:\PythonProjects\ShareMarketBot ; streamlit run dashboard.py
"""

# ============================================================================
# FILES CREATED
# ============================================================================
# 1. dashboard.py (316 lines)
#    - Main Streamlit app
#    - Reads NIFTY50_WEEKLY_*.json
#    - Displays BUY/HOLD/SELL in beautiful tables

# 2. DASHBOARD_README.md
#    - Full documentation
#    - Troubleshooting guide
#    - Feature list

# ============================================================================
# THAT'S ALL YOU NEED!
# ============================================================================
# Run: streamlit run dashboard.py
# That's it! Enjoy your dashboard 🎉
