#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIFTY50 Weekly Recommendations Dashboard
Beautiful frontend to display daily trading recommendations
"""

import streamlit as st
import pandas as pd
import json
import glob
import subprocess
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf

# ============================================================================
# CONFIG
# ============================================================================

BASE_DIR = Path(__file__).parent
ANALYSIS_DIR = BASE_DIR / 'nifty50_analysis'
AUTOMATION_SCRIPT = 'nifty50_weekly_automation.py'
ENHANCED_AUTOMATION_SCRIPT = 'nifty50_weekly_automation_enhanced.py'
INTEGRATED_AUTOMATION_SCRIPT = 'nifty50_weekly_integrated_analysis.py'

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="NIFTY50 Trading Recommendations",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        /* Main title styling */
        .main-title {
            font-size: 3em;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 10px;
        }
        
        /* Section titles */
        .section-title {
            font-size: 1.5em;
            font-weight: bold;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0 15px 0;
            color: white;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .buy-section { background: linear-gradient(90deg, #10b981, #059669); }
        .hold-section { background: linear-gradient(90deg, #f59e0b, #d97706); }
        .sell-section { background: linear-gradient(90deg, #ef4444, #dc2626); }
        
        /* Info boxes */
        .info-box {
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f9ff;
            border-left: 5px solid #0284c7;
            margin-bottom: 20px;
        }
        
        /* Stats cards */
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            font-size: 1.2em;
            margin: 10px;
        }
        
        /* Table styling */
        .dataframe {
            font-size: 0.9em;
        }
        
        /* Timestamp styling */
        .timestamp {
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin: 15px 0;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_todays_json_file():
    """Check if today's JSON file exists, return path if yes"""
    today = datetime.now()

    # Subtract one day using timedelta to get yesterday's datetime object
    yesterday = today - timedelta(days=1)

    # Format the previous day's datetime object into the desired string format
    previous_date_str = yesterday.strftime('%Y%m%d')
    pattern = f"{ANALYSIS_DIR}/NIFTY50_WEEKLY_{previous_date_str}_*.json"
    files = glob.glob(pattern)
    
    if files:
        # Return the latest file if multiple exist
        return sorted(files)[-1]
    return None

def get_todays_enhanced_json_file():
    """Check if today's enhanced JSON file exists, return path if yes"""
    today = datetime.now()

    # Subtract one day using timedelta to get yesterday's datetime object
    yesterday = today - timedelta(days=1)

    # Format the previous day's datetime object into the desired string format
    previous_date_str = yesterday.strftime('%Y%m%d')

    pattern = f"{ANALYSIS_DIR}/NIFTY50_WEEKLY_ENHANCED_{previous_date_str}_*.json"
    files = glob.glob(pattern)
    
    if files:
        # Return the latest file if multiple exist
        return sorted(files)[-1]
    return None

def get_todays_integrated_json_file():
    """Check if today's integrated JSON file exists, return path if yes"""
    today = datetime.now()

    # Subtract one day using timedelta to get yesterday's datetime object
    yesterday = today - timedelta(days=1)

    # Format the previous day's datetime object into the desired string format
    previous_date_str = yesterday.strftime('%Y%m%d')

    pattern = f"{ANALYSIS_DIR}/NIFTY50_INTEGRATED_WEEKLY_{previous_date_str}_*.json"
    files = glob.glob(pattern)
    
    # Filter out REPORTS files (we want the structured JSON, not the text reports)
    files = [f for f in files if 'REPORTS' not in f]
    
    if files:
        # Return the latest file if multiple exist
        return sorted(files)[-1]
    return None

def generate_todays_recommendations():
    """Run automation script to generate today's recommendations"""
    try:
        st.info("⏳ Generating today's recommendations... This may take 2-3 minutes.")
        
        result = subprocess.run(
            [sys.executable, AUTOMATION_SCRIPT],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            st.error(f"Error running automation script: {result.stderr}")
            return None
        
        # Check if file was created
        json_file = get_todays_json_file()
        if json_file:
            st.success("✅ Recommendations generated successfully!")
            return json_file
        else:
            st.error("File generated but not found")
            return None
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def generate_todays_enhanced_recommendations():
    """Run enhanced automation script to generate today's recommendations"""
    try:
        st.info("⏳ Generating enhanced recommendations... This may take 2-3 minutes.")
        
        result = subprocess.run(
            [sys.executable, ENHANCED_AUTOMATION_SCRIPT],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            st.error(f"Error running enhanced automation script: {result.stderr}")
            return None
        
        # Check if file was created
        json_file = get_todays_enhanced_json_file()
        if json_file:
            st.success("✅ Enhanced recommendations generated successfully!")
            return json_file
        else:
            st.error("File generated but not found")
            return None
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def generate_todays_integrated_recommendations():
    """Run integrated automation script to generate today's recommendations"""
    try:
        st.info("⏳ Generating integrated recommendations... This may take 10-15 minutes (21 modules).")
        
        result = subprocess.run(
            [sys.executable, INTEGRATED_AUTOMATION_SCRIPT],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=1200  # 20 minutes timeout for comprehensive analysis
        )
        
        if result.returncode != 0:
            st.error(f"Error running integrated automation script: {result.stderr}")
            return None
        
        # Check if file was created
        json_file = get_todays_integrated_json_file()
        if json_file:
            st.success("✅ Integrated recommendations generated successfully!")
            return json_file
        else:
            st.error("File generated but not found")
            return None
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def load_json_data(file_path):
    """Load and parse JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def prepare_dataframe(recommendations, signal_type):
    """Prepare dataframe for display based on signal type"""
    filtered = [r for r in recommendations if r.get('Signal') == signal_type]
    
    if not filtered:
        return None
    
    df = pd.DataFrame(filtered)
    
    # Select and rename columns for display
    display_cols = {
        'Ticker': 'Stock',
        'Current_Price': 'Price',
        'Trend_Percent': 'Trend %',
        'Momentum_Percent': 'Momentum %',
        'Volatility_Percent': 'Volatility %',
        'Target': 'Target',
        'Stop_Loss': 'Stop Loss',
        'RR_Ratio': 'RR Ratio',
        'Confidence': 'Confidence %'
    }
    
    # Include Buy_Range if it's BUY signal
    if signal_type == 'BUY':
        display_cols['Buy_Range_Low'] = 'Buy Low'
        display_cols['Buy_Range_High'] = 'Buy High'
    
    # Select only available columns
    cols_to_show = [col for col in display_cols.keys() if col in df.columns]
    df_display = df[cols_to_show].copy()
    
    # Rename columns
    df_display = df_display.rename(columns={k: v for k, v in display_cols.items() if k in cols_to_show})
    
    # Format numeric columns
    numeric_cols = df_display.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        if 'Price' in col or 'Target' in col or 'Stop' in col or 'Low' in col or 'High' in col:
            df_display[col] = df_display[col].apply(lambda x: f"₹{x:.2f}")
        elif '%' in col:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}%")
        elif 'Ratio' in col:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}")
    
    return df_display

def search_stock(recommendations, search_ticker):
    """Search for a specific stock in recommendations"""
    if not search_ticker:
        return None
    
    # Normalize search term
    search_ticker = search_ticker.upper().strip()
    
    # Find the stock
    for rec in recommendations:
        ticker = rec.get('Ticker', '').upper()
        if search_ticker in ticker or ticker in search_ticker:
            return rec
    
    return None

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Title
    st.markdown('<div class="main-title">📈 NIFTY50 Weekly Recommendations</div>', unsafe_allow_html=True)
    
    # Search functionality in sidebar
    with st.sidebar:
        st.header("🔍 Stock Search")
        search_query = st.text_input("Enter Stock Ticker (e.g., TCS.NS, RELIANCE.NS)", key="stock_search")
        
        if search_query:
            st.markdown("---")
            st.subheader("Search Results")
    
    # Create tabs for different recommendation types
    tab1, tab2, tab3 = st.tabs(["📊 Standard Analysis", "🚀 Enhanced Analysis", "🎯 Integrated Analysis"])
    
    # ============================================================================
    # TAB 1: STANDARD ANALYSIS (Original functionality)
    # ============================================================================
    with tab1:
        # Get or generate file
        json_file = get_todays_json_file()
        
        if not json_file:
            st.warning("No recommendations available for today")
            if st.button("🔄 Generate Now", key="generate_button"):
                json_file = generate_todays_recommendations()
        
        if json_file:
            # Load data
            data = load_json_data(json_file)
            
            if data:
                metadata = data.get('Metadata', {})
                recommendations = data.get('Recommendations', [])
                
                # Search functionality - display results if search query exists
                if search_query:
                    result = search_stock(recommendations, search_query)
                    with st.sidebar:
                        if result:
                            signal = result.get('Signal', 'Unknown')
                            signal_color = {'BUY': '🟢', 'HOLD': '🟡', 'SELL': '🔴'}.get(signal, '⚪')
                            
                            st.success(f"**Found in Standard Analysis!**")
                            st.markdown(f"### {signal_color} {result.get('Ticker', 'N/A')}")
                            st.markdown(f"**Signal:** {signal}")
                            st.markdown(f"**Price:** ₹{result.get('Current_Price', 0):.2f}")
                            
                            if 'Target' in result:
                                st.markdown(f"**Target:** ₹{result.get('Target', 0):.2f}")
                            if 'Stop_Loss' in result:
                                st.markdown(f"**Stop Loss:** ₹{result.get('Stop_Loss', 0):.2f}")
                            if 'Confidence' in result:
                                st.markdown(f"**Confidence:** {result.get('Confidence', 0):.1f}%")
                            if signal == 'BUY' and 'Buy_Range_Low' in result:
                                st.markdown(f"**Buy Range:** ₹{result.get('Buy_Range_Low', 0):.2f} - ₹{result.get('Buy_Range_High', 0):.2f}")
                        else:
                            st.warning(f"Stock '{search_query}' not found in Standard Analysis")
                
                # Display timestamp
                generated_date = metadata.get('Generated_Date', 'Unknown')
                st.markdown(f'<div class="timestamp">Generated: {generated_date}</div>', unsafe_allow_html=True)
                
                # Signal summary in stats
                signal_summary = metadata.get('Signal_Summary', {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #10b981, #059669); 
                                    padding: 20px; border-radius: 10px; color: white; 
                                    text-align: center; font-size: 1.3em;">
                            <div style="font-size: 0.8em; opacity: 0.9;">🟢 BUY SIGNALS</div>
                            <div style="font-size: 2em; font-weight: bold;">{signal_summary.get('BUY', 0)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #f59e0b, #d97706); 
                                    padding: 20px; border-radius: 10px; color: white; 
                                    text-align: center; font-size: 1.3em;">
                            <div style="font-size: 0.8em; opacity: 0.9;">🟡 HOLD SIGNALS</div>
                            <div style="font-size: 2em; font-weight: bold;">{signal_summary.get('HOLD', 0)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #ef4444, #dc2626); 
                                    padding: 20px; border-radius: 10px; color: white; 
                                    text-align: center; font-size: 1.3em;">
                            <div style="font-size: 0.8em; opacity: 0.9;">🔴 SELL SIGNALS</div>
                            <div style="font-size: 2em; font-weight: bold;">{signal_summary.get('SELL', 0)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # ========== BUY SECTION ==========
                st.markdown('<div class="section-title buy-section">🟢 BUY SIGNALS - Entry Opportunities</div>', 
                           unsafe_allow_html=True)
                
                buy_df = prepare_dataframe(recommendations, 'BUY')
                if buy_df is not None:
                    st.dataframe(buy_df, use_container_width=True, hide_index=True)
                    st.caption(f"✅ {len(buy_df)} stocks showing strong BUY signals")
                else:
                    st.info("No BUY signals available for today")
                
                st.divider()
                
                # ========== HOLD SECTION ==========
                st.markdown('<div class="section-title hold-section">🟡 HOLD SIGNALS - Monitor Positions</div>', 
                           unsafe_allow_html=True)
                
                hold_df = prepare_dataframe(recommendations, 'HOLD')
                if hold_df is not None:
                    st.dataframe(hold_df, use_container_width=True, hide_index=True)
                    st.caption(f"⏸️  {len(hold_df)} stocks recommended to HOLD")
                else:
                    st.info("No HOLD signals available for today")
                
                st.divider()
                
                # ========== SELL SECTION ==========
                st.markdown('<div class="section-title sell-section">🔴 SELL SIGNALS - Exit Positions</div>', 
                           unsafe_allow_html=True)
                
                sell_df = prepare_dataframe(recommendations, 'SELL')
                if sell_df is not None:
                    st.dataframe(sell_df, use_container_width=True, hide_index=True)
                    st.caption(f"⛔ {len(sell_df)} stocks showing SELL signals")
                else:
                    st.info("No SELL signals available for today")
                
                st.divider()
                
                # Footer info
                st.markdown("""
                    <div style="text-align: center; color: #666; margin-top: 30px; font-size: 0.85em;">
                        <p><strong>Disclaimer:</strong> These recommendations are based on technical analysis only. 
                        Always consult with a financial advisor before making investment decisions.</p>
                        <p>Generated using Phase 19.2 + 19.3 Analysis | Real-time data from yfinance</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # ============================================================================
    # TAB 2: ENHANCED ANALYSIS (New functionality)
    # ============================================================================
    with tab2:
        # Get or generate enhanced file
        enhanced_json_file = get_todays_enhanced_json_file()
        
        if not enhanced_json_file:
            st.warning("No enhanced recommendations available for today")
            if st.button("🔄 Generate Enhanced Analysis", key="generate_enhanced_button"):
                enhanced_json_file = generate_todays_enhanced_recommendations()
        
        if enhanced_json_file:
            # Load data
            data = load_json_data(enhanced_json_file)
            
            if data:
                metadata = data.get('Metadata', {})
                recommendations = data.get('Recommendations', [])
                
                # Search functionality - display results if search query exists
                if search_query:
                    result = search_stock(recommendations, search_query)
                    with st.sidebar:
                        if result:
                            signal = result.get('Signal', 'Unknown')
                            signal_color = {'BUY': '🟢', 'HOLD': '🟡', 'SELL': '🔴'}.get(signal, '⚪')
                            
                            st.success(f"**Found in Enhanced Analysis!**")
                            st.markdown(f"### {signal_color} {result.get('Ticker', 'N/A')}")
                            st.markdown(f"**Signal:** {signal}")
                            st.markdown(f"**Price:** ₹{result.get('Current_Price', 0):.2f}")
                            
                            if 'Target' in result:
                                st.markdown(f"**Target:** ₹{result.get('Target', 0):.2f}")
                            if 'Stop_Loss' in result:
                                st.markdown(f"**Stop Loss:** ₹{result.get('Stop_Loss', 0):.2f}")
                            if 'Confidence' in result:
                                st.markdown(f"**Confidence:** {result.get('Confidence', 0):.1f}%")
                            if signal == 'BUY' and 'Buy_Range_Low' in result:
                                st.markdown(f"**Buy Range:** ₹{result.get('Buy_Range_Low', 0):.2f} - ₹{result.get('Buy_Range_High', 0):.2f}")
                            
                            # Enhanced-specific metrics
                            if 'RSI' in result:
                                st.markdown(f"**RSI:** {result.get('RSI', 0):.1f}")
                            if 'Trend_Assessment' in result:
                                st.markdown(f"**Trend:** {result.get('Trend_Assessment', 'N/A')}")
                        else:
                            st.warning(f"Stock '{search_query}' not found in Enhanced Analysis")
                
                # Display timestamp
                generated_date = metadata.get('Generated_Date', 'Unknown')
                st.markdown(f'<div class="timestamp">Generated: {generated_date}</div>', unsafe_allow_html=True)
                
                # Signal summary in stats
                signal_summary = metadata.get('Signal_Summary', {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #10b981, #059669); 
                                    padding: 20px; border-radius: 10px; color: white; 
                                    text-align: center; font-size: 1.3em;">
                            <div style="font-size: 0.8em; opacity: 0.9;">🟢 BUY SIGNALS</div>
                            <div style="font-size: 2em; font-weight: bold;">{signal_summary.get('BUY', 0)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #f59e0b, #d97706); 
                                    padding: 20px; border-radius: 10px; color: white; 
                                    text-align: center; font-size: 1.3em;">
                            <div style="font-size: 0.8em; opacity: 0.9;">🟡 HOLD SIGNALS</div>
                            <div style="font-size: 2em; font-weight: bold;">{signal_summary.get('HOLD', 0)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #ef4444, #dc2626); 
                                    padding: 20px; border-radius: 10px; color: white; 
                                    text-align: center; font-size: 1.3em;">
                            <div style="font-size: 0.8em; opacity: 0.9;">🔴 SELL SIGNALS</div>
                            <div style="font-size: 2em; font-weight: bold;">{signal_summary.get('SELL', 0)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # Info box explaining enhanced analysis
                st.markdown("""
                    <div class="info-box">
                        <strong>🚀 Enhanced Analysis Features:</strong>
                        <ul>
                            <li>Advanced technical indicators (RSI, MACD, Moving Averages)</li>
                            <li>Multi-timeframe trend analysis</li>
                            <li>Comprehensive risk assessment</li>
                            <li>Entry/Exit point recommendations</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                
                # ========== BUY SECTION ==========
                st.markdown('<div class="section-title buy-section">🟢 BUY SIGNALS - Entry Opportunities</div>', 
                           unsafe_allow_html=True)
                
                buy_df = prepare_dataframe(recommendations, 'BUY')
                if buy_df is not None:
                    st.dataframe(buy_df, use_container_width=True, hide_index=True)
                    st.caption(f"✅ {len(buy_df)} stocks showing strong BUY signals with enhanced technical confirmation")
                else:
                    st.info("No BUY signals available for today")
                
                st.divider()
                
                # ========== HOLD SECTION ==========
                st.markdown('<div class="section-title hold-section">🟡 HOLD SIGNALS - Monitor Positions</div>', 
                           unsafe_allow_html=True)
                
                hold_df = prepare_dataframe(recommendations, 'HOLD')
                if hold_df is not None:
                    st.dataframe(hold_df, use_container_width=True, hide_index=True)
                    st.caption(f"⏸️  {len(hold_df)} stocks recommended to HOLD based on enhanced analysis")
                else:
                    st.info("No HOLD signals available for today")
                
                st.divider()
                
                # ========== SELL SECTION ==========
                st.markdown('<div class="section-title sell-section">🔴 SELL SIGNALS - Exit Positions</div>', 
                           unsafe_allow_html=True)
                
                sell_df = prepare_dataframe(recommendations, 'SELL')
                if sell_df is not None:
                    st.dataframe(sell_df, use_container_width=True, hide_index=True)
                    st.caption(f"⛔ {len(sell_df)} stocks showing SELL signals with technical confirmation")
                else:
                    st.info("No SELL signals available for today")
                
                st.divider()
                
                # Footer info
                st.markdown("""
                    <div style="text-align: center; color: #666; margin-top: 30px; font-size: 0.85em;">
                        <p><strong>Disclaimer:</strong> These recommendations are based on enhanced technical analysis. 
                        Always consult with a financial advisor before making investment decisions.</p>
                        <p>Generated using Enhanced Technical Analysis Module | Real-time data from yfinance</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # ============================================================================
    # TAB 3: INTEGRATED ANALYSIS (Comprehensive 21-module analysis)
    # ============================================================================
    with tab3:
        # Get or generate integrated file
        integrated_json_file = get_todays_integrated_json_file()
        
        if not integrated_json_file:
            st.warning("No integrated recommendations available for today")
            if st.button("🔄 Generate Integrated Analysis", key="generate_integrated_button"):
                integrated_json_file = generate_todays_integrated_recommendations()
        
        if integrated_json_file:
            # Load data - integrated analysis has different structure (text reports, not structured JSON)
            try:
                with open(integrated_json_file, 'r') as f:
                    data = json.load(f)
                
                # Integrated analysis returns array of structured objects with prices already included
                recommendations = []
                if isinstance(data, list) and len(data) > 0:
                    # Check if data is already structured (has 'ticker' field) or old text format
                    if isinstance(data[0], dict) and 'ticker' in data[0]:
                        # New structured format with prices already included
                        recommendations = data
                        st.success(f"✅ Loaded {len(recommendations)} stocks with prices!")
                    else:
                        # Old text format - show error message
                        st.error("⚠️ Old data format detected. Please regenerate the integrated analysis to get prices.")
                        recommendations = []
                    
                    # Create metadata from the data
                    metadata = {
                        'Generated_Date': datetime.now().isoformat(),
                        'Total_Stocks': len(recommendations),
                        'Signal_Summary': {
                            'ACCUMULATE': sum(1 for r in recommendations if r.get('decision') == 'InvestmentDecision.ACCUMULATE'),
                            'HOLD': sum(1 for r in recommendations if r.get('decision') == 'InvestmentDecision.HOLD'),
                            'AVOID': sum(1 for r in recommendations if r.get('decision') == 'InvestmentDecision.AVOID')
                        }
                    }
                    
                    # Transform integrated data to match dashboard format
                    transformed_recs = []
                    for rec in recommendations:
                        # Map integrated analysis fields to dashboard format
                        decision = rec.get('decision', '').replace('InvestmentDecision.', '')
                        transformed = {
                            'Ticker': rec.get('ticker', 'N/A'),
                            'Signal': decision if decision in ['ACCUMULATE', 'HOLD', 'AVOID'] else 'AVOID',
                            'Current_Price': rec.get('current_price', 0),
                            'Target': rec.get('target_price', 0),
                            'Stop_Loss': rec.get('stop_loss', 0),
                            'Confidence': rec.get('scores', {}).get('confidence', 0),
                            'Fundamental_Score': rec.get('scores', {}).get('fundamental_score', 0),
                            'Technical_Score': rec.get('scores', {}).get('technical_score', 0)
                        }
                        transformed_recs.append(transformed)
                    
                    # Search functionality
                    if search_query:
                        result = search_stock(transformed_recs, search_query)
                        with st.sidebar:
                            if result:
                                signal = result.get('Signal', 'Unknown')
                                signal_color = {'ACCUMULATE': '🟢', 'HOLD': '🟡', 'AVOID': '🔴'}.get(signal, '⚪')
                                
                                st.success(f"**Found in Integrated Analysis!**")
                                st.markdown(f"### {signal_color} {result.get('Ticker', 'N/A')}")
                                st.markdown(f"**Decision:** {signal}")
                                st.markdown(f"**Price:** ₹{result.get('Current_Price', 0):.2f}")
                                
                                if 'Target' in result and result['Target'] > 0:
                                    st.markdown(f"**Target:** ₹{result.get('Target', 0):.2f}")
                                if 'Stop_Loss' in result and result['Stop_Loss'] > 0:
                                    st.markdown(f"**Stop Loss:** ₹{result.get('Stop_Loss', 0):.2f}")
                                if 'Confidence' in result:
                                    st.markdown(f"**Confidence:** {result.get('Confidence', 0):.1f}%")
                                
                                # Integrated-specific metrics
                                if 'Fundamental_Score' in result:
                                    st.markdown(f"**Fundamental Score:** {result.get('Fundamental_Score', 0):.1f}/100")
                                if 'Technical_Score' in result:
                                    st.markdown(f"**Technical Score:** {result.get('Technical_Score', 0):.1f}/100")
                            else:
                                st.warning(f"Stock '{search_query}' not found in Integrated Analysis")
                    
                    # Display timestamp
                    st.markdown(f'<div class="timestamp">Generated: {metadata.get("Generated_Date", "Unknown")}</div>', unsafe_allow_html=True)
                    
                    # Signal summary in stats with detailed breakdown
                    signal_summary = metadata.get('Signal_Summary', {})
                    total_stocks = metadata.get('Total_Stocks', 0)
                    
                    st.info(f"📊 **Total Stocks Analyzed:** {total_stocks} | "
                           f"ACCUMULATE: {signal_summary.get('ACCUMULATE', 0)} | "
                           f"HOLD: {signal_summary.get('HOLD', 0)} | "
                           f"AVOID: {signal_summary.get('AVOID', 0)}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #10b981, #059669); 
                                        padding: 20px; border-radius: 10px; color: white; 
                                        text-align: center; font-size: 1.3em;">
                                <div style="font-size: 0.8em; opacity: 0.9;">🟢 ACCUMULATE</div>
                                <div style="font-size: 2em; font-weight: bold;">{signal_summary.get('ACCUMULATE', 0)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #f59e0b, #d97706); 
                                        padding: 20px; border-radius: 10px; color: white; 
                                        text-align: center; font-size: 1.3em;">
                                <div style="font-size: 0.8em; opacity: 0.9;">🟡 HOLD</div>
                                <div style="font-size: 2em; font-weight: bold;">{signal_summary.get('HOLD', 0)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #ef4444, #dc2626); 
                                        padding: 20px; border-radius: 10px; color: white; 
                                        text-align: center; font-size: 1.3em;">
                                <div style="font-size: 0.8em; opacity: 0.9;">🔴 AVOID</div>
                                <div style="font-size: 2em; font-weight: bold;">{signal_summary.get('AVOID', 0)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Info box explaining integrated analysis
                    st.markdown("""
                        <div class="info-box">
                            <strong>🎯 Integrated Analysis - 21 Modules:</strong>
                            <ul>
                                <li>Enhanced Fundamental Analysis (ROE, ROCE, Margins, Growth)</li>
                                <li>Enhanced Technical Analysis (Breakouts, Patterns, Indicators)</li>
                                <li>Market Regime Filter (Bull/Bear/Sideways detection)</li>
                                <li>Event Risk Analysis (Earnings, News, Corporate actions)</li>
                                <li>Drawdown Modeling (Risk assessment)</li>
                                <li>Confidence Quantification (Historical win rates)</li>
                                <li>Two-Layer Decision Engine (Investment View + Trade Setup)</li>
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # ========== ACCUMULATE SECTION ==========
                    st.markdown('<div class="section-title buy-section">🟢 ACCUMULATE - Strong Long-term Investment</div>', 
                               unsafe_allow_html=True)
                    
                    accumulate_stocks = [r for r in transformed_recs if r['Signal'] == 'ACCUMULATE']
                    if accumulate_stocks:
                        df = pd.DataFrame(accumulate_stocks)
                        display_df = df[['Ticker', 'Current_Price', 'Target', 'Stop_Loss', 'Fundamental_Score', 'Technical_Score', 'Confidence']].copy()
                        display_df.columns = ['Stock', 'Price', 'Target', 'Stop Loss', 'Fund Score', 'Tech Score', 'Confidence']
                        
                        # Format columns
                        for col in ['Price', 'Target', 'Stop Loss']:
                            if col in display_df.columns:
                                display_df[col] = display_df[col].apply(lambda x: f"₹{x:.2f}" if x > 0 else "-")
                        for col in ['Fund Score', 'Tech Score']:
                            if col in display_df.columns:
                                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}")
                        if 'Confidence' in display_df.columns:
                            display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.1f}%")
                        
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                        st.caption(f"✅ {len(accumulate_stocks)} stocks recommended for accumulation")
                    else:
                        st.info("No ACCUMULATE signals available")
                    
                    st.divider()
                    
                    # ========== HOLD SECTION ==========
                    st.markdown('<div class="section-title hold-section">🟡 HOLD - Monitor & Wait</div>', 
                               unsafe_allow_html=True)
                    
                    hold_stocks = [r for r in transformed_recs if r['Signal'] == 'HOLD']
                    if hold_stocks:
                        df = pd.DataFrame(hold_stocks)
                        display_df = df[['Ticker', 'Current_Price', 'Fundamental_Score', 'Technical_Score', 'Confidence']].copy()
                        display_df.columns = ['Stock', 'Price', 'Fund Score', 'Tech Score', 'Confidence']
                        
                        # Format columns
                        if 'Price' in display_df.columns:
                            display_df['Price'] = display_df['Price'].apply(lambda x: f"₹{x:.2f}")
                        for col in ['Fund Score', 'Tech Score']:
                            if col in display_df.columns:
                                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}")
                        if 'Confidence' in display_df.columns:
                            display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.1f}%")
                        
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                        st.caption(f"⏸️  {len(hold_stocks)} stocks recommended to HOLD")
                    else:
                        st.info("No HOLD signals available")
                    
                    st.divider()
                    
                    # ========== AVOID SECTION ==========
                    st.markdown('<div class="section-title sell-section">🔴 AVOID - Weak Fundamentals or Setup</div>', 
                               unsafe_allow_html=True)
                    
                    avoid_stocks = [r for r in transformed_recs if r['Signal'] == 'AVOID']
                    if avoid_stocks:
                        df = pd.DataFrame(avoid_stocks)
                        display_df = df[['Ticker', 'Current_Price', 'Fundamental_Score', 'Technical_Score']].copy()
                        display_df.columns = ['Stock', 'Price', 'Fund Score', 'Tech Score']
                        
                        # Format columns
                        if 'Price' in display_df.columns:
                            display_df['Price'] = display_df['Price'].apply(lambda x: f"₹{x:.2f}" if x > 0 else "N/A")
                        for col in ['Fund Score', 'Tech Score']:
                            if col in display_df.columns:
                                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}")
                        
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                        st.caption(f"⛔ {len(avoid_stocks)} stocks showing AVOID signals")
                    else:
                        st.info("No AVOID signals")
                    
                    st.divider()
                    
                    # Footer info
                    st.markdown("""
                        <div style="text-align: center; color: #666; margin-top: 30px; font-size: 0.85em;">
                            <p><strong>Disclaimer:</strong> These recommendations combine fundamental + technical analysis with 21 specialized modules. 
                            Always consult with a financial advisor before making investment decisions.</p>
                            <p>Generated using Integrated Analysis (21 Modules) | Fundamental data from CSV + yfinance | Technical data from yfinance</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Error loading integrated analysis: {str(e)}")

if __name__ == "__main__":
    main()
