# Stock Universe Configuration

This directory contains centralized stock universe configurations used across all analysis scripts.

## Files

### `stock_universe.py`
The main configuration file that contains the list of stocks to be analyzed.

**All analysis scripts now read from this single source:**
- `nifty50_weekly_automation.py` (Standard Analysis)
- `nifty50_weekly_automation_enhanced.py` (Enhanced Analysis)
- `nifty50_weekly_integrated_analysis.py` (Integrated Analysis)

## Usage

### Adding/Removing Stocks

To modify the stock universe for all analysis scripts:

1. Edit `stock_universe.py`
2. Add or remove tickers from the `NIFTY50_STOCKS` list
3. Save the file
4. All analysis scripts will automatically use the updated list

### Example

```python
from universes.stock_universe import get_stock_universe

# Get the current stock list
stocks = get_stock_universe()
print(f"Analyzing {len(stocks)} stocks")
```

## Benefits

✅ **Consistency**: All scripts analyze the same set of stocks  
✅ **Maintainability**: Update stocks in one place instead of three  
✅ **Scalability**: Easy to add new analysis scripts that use the same universe  
✅ **Version Control**: Track changes to your stock universe over time  

## Stock Format

Stocks should be in Yahoo Finance format with `.NS` suffix for NSE stocks:
- ✅ `RELIANCE.NS`
- ✅ `TCS.NS`
- ❌ `RELIANCE` (missing .NS)
