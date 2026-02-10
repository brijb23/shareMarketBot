# 📈 Stock Market Analysis Bot

Automated daily stock analysis system with 21-module comprehensive analysis engine and real-time dashboard.

## 🌟 Features

- **Standard Analysis**: Technical indicators, trend analysis, momentum scoring
- **Enhanced Analysis**: Advanced pattern recognition, breakout detection
- **Integrated Analysis**: 21-module comprehensive system including:
  - Enhanced Fundamental Analysis
  - Market Regime Detection
  - Event Risk Analysis
  - Drawdown Modeling
  - Confidence Quantification
  - Two-Layer Decision Engine

- **Interactive Dashboard**: Streamlit-based web interface
- **Automated Daily Runs**: GitHub Actions scheduled workflow
- **Centralized Stock Universe**: Single source for all stock lists

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/shareMarketBot.git
cd shareMarketBot

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run analysis manually
python nifty50_weekly_integrated_analysis.py

# Start dashboard
streamlit run dashboard.py
```

### Cloud Deployment (Recommended)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete cloud setup instructions.

**Quick steps:**
1. Push code to GitHub
2. Deploy dashboard to Streamlit Cloud (free)
3. GitHub Actions runs analysis daily at midnight automatically
4. Dashboard updates automatically with fresh data

## 📊 Analysis Types

### 1. Standard Analysis
- File: `nifty50_weekly_automation.py`
- Duration: ~2-3 minutes
- Output: BUY/SELL/HOLD signals

### 2. Enhanced Analysis  
- File: `nifty50_weekly_automation_enhanced.py`
- Duration: ~3-5 minutes
- Output: Enhanced signals with pattern detection

### 3. Integrated Analysis
- File: `nifty50_weekly_integrated_analysis.py`
- Duration: ~10-15 minutes
- Output: ACCUMULATE/HOLD/AVOID with comprehensive scoring

## 🗂️ Project Structure

```
shareMarketBot/
├── .github/workflows/          # GitHub Actions automation
│   ├── daily_analysis.yml      # Scheduled daily run
│   └── manual_analysis.yml     # Manual trigger
├── src/                        # Analysis modules (21 modules)
│   ├── enhanced_fundamental_analyzer.py
│   ├── enhanced_technical_analyzer.py
│   ├── market_regime_filter.py
│   └── ... (18 more modules)
├── universes/                  # Stock configuration
│   └── stock_universe.py       # Centralized stock list (503 stocks)
├── nifty50_analysis/          # Output folder (auto-generated)
│   ├── *.json                 # Analysis results
│   ├── *.csv                  # Tabular data
│   └── *.md                   # Reports
├── data/                      # Input data
│   ├── fundamentals/          # Company fundamentals
│   └── prices/                # Historical prices
├── dashboard.py               # Streamlit dashboard
├── nifty50_weekly_automation.py
├── nifty50_weekly_automation_enhanced.py
├── nifty50_weekly_integrated_analysis.py
└── requirements.txt
```

## 🔧 Configuration

### Adding/Removing Stocks

Edit `universes/stock_universe.py`:

```python
NIFTY50_STOCKS = [
    'RELIANCE.NS',
    'TCS.NS',
    'INFY.NS',
    # Add more stocks here
]
```

All three analysis scripts automatically use this list.

### Changing Schedule

Edit `.github/workflows/daily_analysis.yml`:

```yaml
schedule:
  - cron: '0 0 * * *'  # Midnight UTC
  # Change to your preferred time
```

## 📱 Dashboard

Access your dashboard at:
- **Local**: http://localhost:8501
- **Cloud**: https://your-app.streamlit.app

Features:
- 🔍 Real-time stock search
- 📊 Three analysis tabs (Standard, Enhanced, Integrated)
- 📈 Interactive tables with sorting/filtering
- 💹 Price updates and target levels
- 🎯 Confidence scores and signals

## 🤖 Automation

### GitHub Actions (Cloud - Recommended)
- ✅ Runs daily at midnight UTC
- ✅ Commits results to repository
- ✅ Completely free
- ✅ Works on any platform
- ✅ View logs in Actions tab

### Manual Trigger
GitHub Actions → Manual Analysis Trigger → Run workflow

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete cloud deployment guide
- [universes/README.md](universes/README.md) - Stock universe configuration
- [DASHBOARD_README.md](DASHBOARD_README.md) - Dashboard usage guide

## 🧪 Testing

```bash
# Run a quick test
python -c "from universes.stock_universe import get_stock_count; print(f'Analyzing {get_stock_count()} stocks')"

# Test individual analysis
python nifty50_weekly_automation.py
```

## 📊 Sample Output

```
ACCUMULATE: 45 stocks
HOLD: 123 stocks  
AVOID: 335 stocks

Top ACCUMULATE picks:
- RELIANCE.NS (₹2,450.50) - Target: ₹2,850
- TCS.NS (₹3,850.25) - Target: ₹4,200
- INFY.NS (₹1,425.75) - Target: ₹1,650
```

## 🔐 Security

- No API keys required for basic functionality
- Stock data from yfinance (free)
- Fundamental data from local CSV files
- GitHub Actions uses automatic GITHUB_TOKEN

## 🛠️ Troubleshooting

### Analysis not running
- Check GitHub Actions tab for errors
- Verify requirements.txt is up to date
- Ensure internet connection for stock data

### Dashboard shows old data
- Refresh browser (Ctrl+R)
- Check if new analysis files were generated
- Verify file paths in dashboard.py

### Import errors
```bash
pip install -r requirements.txt --upgrade
```

## 📈 Performance

- **503 stocks** analyzed daily
- **Standard**: ~2-3 minutes
- **Enhanced**: ~3-5 minutes  
- **Integrated**: ~10-15 minutes
- **Total**: ~20 minutes for all three

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Always do your own research before making investment decisions.

## ⚠️ Disclaimer

This software is provided for informational purposes only. It does not constitute financial advice. Always consult with a qualified financial advisor before making investment decisions. Past performance does not guarantee future results.

## 🙏 Acknowledgments

- Data: Yahoo Finance (yfinance)
- Framework: Streamlit
- Automation: GitHub Actions
- Analysis: 21 custom modules

---

**Made with ❤️ for automated stock analysis**

For support and questions, please open an issue on GitHub.
