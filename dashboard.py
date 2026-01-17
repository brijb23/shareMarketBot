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
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIG
# ============================================================================

BASE_DIR = Path(__file__).parent
ANALYSIS_DIR = BASE_DIR / 'nifty50_analysis'
AUTOMATION_SCRIPT = 'nifty50_weekly_automation.py'

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
    today = datetime.now().strftime('%Y%m%d')
    pattern = f"{ANALYSIS_DIR}/NIFTY50_WEEKLY_{today}_*.json"
    files = glob.glob(pattern)
    
    if files:
        # Return the latest file if multiple exist
        return sorted(files)[-1]
    return None

def generate_todays_recommendations():
    """Run automation script to generate today's recommendations"""
    try:
        st.info("⏳ Generating today's recommendations... This may take 2-3 minutes.")
        
        result = subprocess.run(
            f"python {AUTOMATION_SCRIPT}",
            shell=True,
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

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Title
    st.markdown('<div class="main-title">📈 NIFTY50 Weekly Recommendations</div>', unsafe_allow_html=True)
    
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

if __name__ == "__main__":
    main()
