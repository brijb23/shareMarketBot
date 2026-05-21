#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIFTY50 WEEKLY INTEGRATED ANALYSIS
=====================================
Complete integration of all 21 analysis modules from src/

Pipeline Flow:
1. Market Regime Detection → Are we in TRENDING/RANGING/RISK_OFF?
2. Technical Analysis → Price trend + momentum confirmation
3. Enhanced Fundamental Analysis → Sector-weighted business quality
4. Event Risk Analysis → Upcoming catalysts/risks
5. Convergence Detection → Multi-timeframe alignment
6. Volatility Analysis → Risk-adjusted scoring
7. Drawdown Modeling → Max loss potential
8. Confidence Quantification → Combine all signals
9. Decision Engine → Final investment decision
10. Two-Layer Output → Investment view + Trade setup

OUTPUT:
- Comprehensive JSON with all analysis layers
- Professional investment thesis (bull/bear case)
- Tactical trade setup with confirmations
- Risk-reward optimization
- Scenario analysis (best/base/worst)

Author: Integrated Analysis System
Date: 2026
"""

import os
import json
import csv
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from pathlib import Path
import traceback
import warnings
import sys

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Add src to path for module imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    # Core data structures and configuration
    from src.data_models import FundamentalMetrics, TechnicalMetrics, RiskAssessment, StockAnalysis, Decision
    from src.constants import FUNDAMENTAL_THRESHOLDS, TECHNICAL_THRESHOLDS
    
    # Core analysis engines
    from src.technical_analysis import TechnicalAnalyzer
    from src.fundamental_analysis import FundamentalAnalyzer
    from src.analysis_engine import StockAnalysisEngine
    from src.decision_engine import DecisionEngine
    from src.stock_classifier import StockClassifier
    
    # Enhanced analyzers
    from src.enhanced_fundamental_analyzer import EnhancedFundamentalAnalyzer, StockCategory
    from src.enhanced_technical_analyzer import EnhancedTechnicalAnalyzer, SetupType as TechSetupType
    
    # Risk and filter modules
    from src.market_regime_filter import MarketRegimeFilter, MarketRegimeType
    from src.event_risk_analyzer import EventRiskAnalyzer
    from src.convergence_detector import ConvergenceDetector
    from src.volatility_adjusted_scoring import VolatilityAdjustedScoring
    from src.drawdown_modeler import DrawdownModeler
    
    # Confidence and decision modules
    from src.confidence_quantifier import ConfidenceQuantifier, SetupType as ConfSetupType
    from src.data_confidence_state import DataConfidenceState, DataConfidenceDetector, ConfidenceCapEngine
    from src.uncertainty_aware_decision import UncertaintyAwareDecisionEngine
    from src.two_layer_output import TwoLayerOutputFormatter
    from src.refactored_decision_engine import RefactoredDecisionEngine
    
    # Diagnostics
    from src.phase17_5_diagnostics import DiagnosticsCollector
    
    MODULES_LOADED = True
except ImportError as e:
    print(f"Warning: Could not import all modules. Some functionality will be limited. Error: {e}")
    MODULES_LOADED = False

# ============================================================================
# CONFIG
# ============================================================================

# Import centralized stock universe
from universes.stock_universe import get_stock_universe

class Config:
    """Configuration for integrated analysis"""
    
    NIFTY50_STOCKS = get_stock_universe()  # Load from centralized configuration
    
    # Old hardcoded list (kept for reference, not used):
    _OLD_STOCKS = [
'IFCI.NS', 
'FORCEMOT.NS',
'SBFC.NS',
'HINDCOPPER.NS',
'BSE.NS',
'PREMIERENE.NS',
'IREDA.NS',
'HINDZINC.NS',
'SARDAEN.NS',
'ANANTRAJ.NS',
'PFC.NS',
'SJVN.NS',
'HOMEFIRST.NS',
'COALINDIA.NS',
'CHENNPETRO.NS',
'VTL.NS',
'LINDEINDIA.NS',
'VEDL.NS',
'ABLBL.NS',
'INDUSINDBK.NS',
'MANAPPURAM.NS',
'GODFRYPHLP.NS',
'TATASTEEL.NS',
'SAIL.NS',
'IEX.NS',
'ASIANPAINT.NS',
'GMDCLTD.NS',
'MAHABANK.NS',
'MUTHOOTFIN.NS',
'JSWSTEEL.NS',
'BALKRISIND.NS',
'BLUEJET.NS',
'HINDALCO.NS',
'MCX.NS',
'EMAMILTD.NS',
'COLPAL.NS',
'3MINDIA.NS',
'TORNTPOWER.NS',
'TRENT.NS',
'DEVYANI.NS',
'BRIGADE.NS',
'RECLTD.NS',
'NAVINFLUOR.NS',
'ATUL.NS',
'MRPL.NS',
'NLCINDIA.NS',
'NMDC.NS',
'JWL.NS',
'JYOTICNC.NS',
'WAAREEENER.NS',
'JSWCEMENT.NS',
'LEMONTREE.NS',
'PIIND.NS',
'AIIL.NS',
'MEDANTA.NS',
'M&MFIN.NS',
'ANGELONE.NS',
'GAIL.NS',
'GLAND.NS',
'MRF.NS',
'ULTRACEMCO.NS',
'HINDUNILVR.NS',
'ALKEM.NS',
'DCMSHRIRAM.NS',
'IRFC.NS',
'TATAPOWER.NS',
'SBIN.NS',
'PTCIL.NS',
'BPCL.NS',
'HAL.NS',
'SCHAEFFLER.NS',
'NETWEB.NS',
'UNIONBANK.NS',
'OIL.NS',
'KAYNES.NS',
'MANYAVAR.NS',
'GRSE.NS',
'JINDALSTEL.NS',
'HUDCO.NS',
'HYUNDAI.NS',
'TATACONSUM.NS',
'GESHIP.NS',
'NSLNISP.NS',
'LODHA.NS',
'PIDILITIND.NS',
'MMTC.NS',
'JSWENERGY.NS',
'ENGINERSIN.NS',
'ICICIBANK.NS',
'SYNGENE.NS',
'TCS.NS',
'SAGILITY.NS',
'IKS.NS',
'ADANIENT.NS',
'NESTLEIND.NS',
'EXIDEIND.NS',
'SCI.NS',
'CONCORDBIO.NS',
'SBILIFE.NS',
'AUBANK.NS',
'CEATLTD.NS',
'GRASIM.NS',
'GODREJCP.NS',
'MAZDOCK.NS',
'MGL.NS',
'ATHERENERG.NS',
'ABBOTINDIA.NS',
'BDL.NS',
'GICRE.NS',
'AIAENG.NS',
'ICICIGI.NS',
'DALBHARAT.NS',
'COFORGE.NS',
'VBL.NS',
'NATIONALUM.NS',
'ADANIPOWER.NS',
'CENTRALBK.NS',
'APLAPOLLO.NS',
'ZENSARTECH.NS',
'SAPPHIRE.NS',
'BHARTIARTL.NS',
'BANKBARODA.NS',
'NCC.NS',
'KPRMILL.NS',
'IOB.NS',
'DMART.NS',
'KEC.NS',
'KIRLOSBROS.NS',
'IDBI.NS',
'CDSL.NS',
'ADANIPORTS.NS',
'PNBHOUSING.NS',
'NIACL.NS',
'GLAXO.NS',
'SHREECEM.NS',
'KEI.NS',
'MANKIND.NS',
'IGIL.NS',
'TITAN.NS',
'MARUTI.NS',
'HDFCLIFE.NS',
'INDIAMART.NS',
'ONGC.NS',
'JUBLFOOD.NS',
'RKFORGE.NS',
'INDIACEM.NS',
'INDGN.NS',
'AADHARHFC.NS',
'RELIANCE.NS',
'ABCAPITAL.NS',
'BHARATFORG.NS',
'UCOBANK.NS',
'NHPC.NS',
'TATACHEM.NS',
'NTPC.NS',
'AMBUJACEM.NS',
'YESBANK.NS',
'IOC.NS',
'DRREDDY.NS',
'WIPRO.NS',
'IRCON.NS',
'RVNL.NS',
'RAILTEL.NS',
'BEML.NS',
'ACC.NS',
'ATGL.NS',
'THELEELA.NS',
'NUVOCO.NS',
'MARICO.NS',
'PNB.NS',
'HINDPETRO.NS',
'BAJAJFINSV.NS',
'DABUR.NS',
'FLUOROCHEM.NS',
'JIOFIN.NS',
'LICI.NS',
'SHYAMMETL.NS',
'ECLERX.NS',
'POWERGRID.NS',
'JSL.NS',
'SUNPHARMA.NS',
'GLENMARK.NS',
'HCLTECH.NS',
'KOTAKBANK.NS',
'UPL.NS',
'PAGEIND.NS',
'ETERNAL.NS',
'BANKINDIA.NS',
'CLEAN.NS',
'SRF.NS',
'CHOLAHLDNG.NS',
'ITC.NS',
'AKZOINDIA.NS',
'AXISBANK.NS',
'ZYDUSLIFE.NS',
'KPIL.NS',
'SUZLON.NS',
'LUPIN.NS',
'VOLTAS.NS',
'JINDALSAW.NS',
'M&M.NS',
'GMRAIRPORT.NS',
'TECHM.NS',
'DEEPAKFERT.NS',
'MINDACORP.NS',
'AKUMS.NS',
'CRISIL.NS',
'CANFINHOME.NS',
'TIMKEN.NS',
'APOLLOHOSP.NS',
'SUPREMEIND.NS',
'PGEL.NS',
'KARURVYSYA.NS',
'APOLLOTYRE.NS',
'TATAINVEST.NS',
'IDEA.NS',
'INDIGO.NS',
'RITES.NS',
'CONCOR.NS',
'RBLBANK.NS',
'OFSS.NS',
'INTELLECT.NS',
'HEXT.NS',
'HSCL.NS',
'OLAELEC.NS',
'BIKAJI.NS',
'KAJARIACER.NS',
'SUNTV.NS',
'BAJAJHFL.NS',
'AAVAS.NS',
'LT.NS',
'TVSMOTOR.NS',
'CCL.NS',
'ABFRL.NS',
'COCHINSHIP.NS',
'FIVESTAR.NS',
'VGUARD.NS',
'CIPLA.NS',
'BANDHANBNK.NS',
'VENTIVE.NS',
'EIHOTEL.NS',
'MAXHEALTH.NS',
'TATATECH.NS',
'GODREJAGRO.NS',
'RCF.NS',
'J&KBANK.NS',
'UNITDSPR.NS',
'APTUS.NS',
'ADANIGREEN.NS',
'PATANJALI.NS',
'TECHNOE.NS',
'CANBK.NS',
'TATAELXSI.NS',
'LATENTVIEW.NS',
'APLLTD.NS',
'BEL.NS',
'TITAGARH.NS',
'JYOTHYLAB.NS',
'IRCTC.NS',
'HDFCBANK.NS',
'SUMICHEM.NS',
'JKTYRE.NS',
'ICICIPRULI.NS',
'ABSLAMC.NS',
'NUVAMA.NS',
'FACT.NS',
'INDUSTOWER.NS',
'PETRONET.NS',
'LTFOODS.NS',
'TATACOMM.NS',
'ASHOKLEY.NS',
'MOTHERSON.NS',
'NTPCGREEN.NS',
'CARBORUNIV.NS',
'SWIGGY.NS',
'SUNDRMFAST.NS',
'NYKAA.NS',
'NAUKRI.NS',
'AEGISLOG.NS',
'LTIM.NS',
'BLUESTARCO.NS',
'SUNDARMFIN.NS',
'VIJAYA.NS',
'BBTC.NS',
'360ONE.NS',
'PPLPHARMA.NS',
'INOXWIND.NS',
'MPHASIS.NS',
'PHOENIXLTD.NS',
'ANANDRATHI.NS',
'KSB.NS',
'EIDPARRY.NS',
'BLUEDART.NS',
'FINPIPE.NS',
'ITI.NS',
'AJANTPHARM.NS',
'RAINBOW.NS',
'CHOLAFIN.NS',
'HEG.NS',
'INDHOTEL.NS',
'TRITURBINE.NS',
'WOCKPHARMA.NS',
'ADANIENSOL.NS',
'INDIANB.NS',
'RPOWER.NS',
'TORNTPHARM.NS',
'VMM.NS',
'SONACOMS.NS',
'ALKYLAMINE.NS',
'DATAPATTNS.NS',
'CROMPTON.NS',
'ASTRAL.NS',
'SHRIRAMFIN.NS',
'DIXON.NS',
'SCHNEIDER.NS',
'BRITANNIA.NS',
'MFSL.NS',
'ABB.NS',
'IIFL.NS',
'ESCORTS.NS',
'SONATSOFTW.NS',
'GILLETTE.NS',
'PFIZER.NS',
'CASTROLIND.NS',
'CESC.NS',
'AARTIIND.NS',
'SOBHA.NS',
'ERIS.NS',
'POLYCAB.NS',
'CYIENT.NS',
'INOXINDIA.NS',
'RAMCOCEM.NS',
'IRB.NS',
'CAPLIPOINT.NS',
'LTF.NS',
'HONASA.NS',
'EICHERMOT.NS',
'HEROMOTOCO.NS',
'FEDERALBNK.NS',
'KIMS.NS',
'DOMS.NS',
'BAJAJ-AUTO.NS',
'TTML.NS',
'LTTS.NS',
'AGARWALEYE.NS',
'BOSCHLTD.NS',
'BERGEPAINT.NS',
'PGHH.NS',
'SBICARD.NS',
'LLOYDSME.NS',
'CAMPUS.NS',
'KPITTECH.NS',
'KFINTECH.NS',
'BAYERCROP.NS',
'ENRIN.NS',
'POLICYBZR.NS',
'BAJFINANCE.NS',
'TMPV.NS',
'KALYANKJIL.NS',
'SAMMAANCAP.NS',
'USHAMART.NS',
'INFY.NS',
'HAVELLS.NS',
'OLECTRA.NS',
'ZEEL.NS',
'WELSPUNLIV.NS',
'CHALET.NS',
'GODIGIT.NS',
'RHIM.NS',
'NEULANDLAB.NS',
'DEEPAKNTR.NS',
'COROMANDEL.NS',
'STARHEALTH.NS',
'ELGIEQUIP.NS',
'ARE&M.NS',
'JMFINANCIL.NS',
'FORTIS.NS',
'MOTILALOFS.NS',
'CGCL.NS',
'JBCHEPHARM.NS',
'SOLARINDS.NS',
'ACMESOLAR.NS',
'CERA.NS',
'DBREALTY.NS',
'GRANULES.NS',
'ALOKINDS.NS',
'NBCC.NS',
'PERSISTENT.NS',
'IDFCFIRSTB.NS',
'WELCORP.NS',
'AEGISVOPAK.NS',
'GUJGASLTD.NS',
'GRAPHITE.NS',
'AWL.NS',
'JSWINFRA.NS',
'RRKABEL.NS',
'IGL.NS',
'HDFCAMC.NS',
'REDINGTON.NS',
'PCBL.NS',
'POLYMED.NS',
'PAYTM.NS',
'LICHSGFIN.NS',
'CGPOWER.NS',
'NIVABUPA.NS',
'HAPPSTMNDS.NS',
'BLS.NS',
'CHOICEIN.NS',
'HONAUT.NS',
'GPIL.NS',
'ZENTEC.NS',
'OBEROIRLTY.NS',
'UTIAMC.NS',
'BSOFT.NS',
'NH.NS',
'DLF.NS',
'FSL.NS',
'BATAINDIA.NS',
'AFCONS.NS',
'FINCABLES.NS',
'JUBLINGREA.NS',
'JPPOWER.NS',
'ENDURANCE.NS',
'METROPOLIS.NS',
'UBL.NS',
'WHIRLPOOL.NS',
'SIEMENS.NS',
'ITCHOTELS.NS',
'MSUMI.NS',
'NAVA.NS',
'PRAJIND.NS',
'CRAFTSMAN.NS',
'JUBLPHARMA.NS',
'ZFCVINDIA.NS',
'DIVISLAB.NS',
'TIINDIA.NS',
'NAM-INDIA.NS',
'TARIL.NS',
'GSPL.NS',
'HBLENGINE.NS',
'IPCALAB.NS',
'NEWGEN.NS',
'SYRMA.NS',
'CENTURYPLY.NS',
'JKCEMENT.NS',
'BASF.NS',
'JBMA.NS',
'GODREJIND.NS',
'TRIDENT.NS',
'TBOTEK.NS',
'ASAHIINDIA.NS',
'CAMS.NS',
'ASTRAZEN.NS',
'DELHIVERY.NS',
'ACE.NS',
'THERMAX.NS',
'BIOCON.NS',
'ASTERDM.NS',
'ONESOURCE.NS',
'PVRINOX.NS',
'AUROPHARMA.NS',
'CREDITACC.NS',
'POONAWALLA.NS',
'MAHSEAMLES.NS',
'MAPMYINDIA.NS',
'BHEL.NS',
'LALPATHLAB.NS',
'KIRLOSENG.NS',
'HFCL.NS',
'CHAMBLFERT.NS',
'BAJAJHLDNG.NS',
'POWERINDIA.NS',
'TRIVENI.NS',
'ELECON.NS',
'EMCURE.NS',
'BALRAMCHIN.NS',
'FIRSTCRY.NS',
'GODREJPROP.NS',
'SAREGAMA.NS',
'AFFLE.NS',
'BHARTIHEXA.NS',
'NATCOPHARM.NS',
'SAILIFE.NS',
'ABREL.NS',
'CUMMINSIND.NS',
'AMBER.NS',
'UNOMINDA.NS',
'GRAVITA.NS',
'RADICO.NS',
'SWANCORP.NS',
'LAURUSLABS.NS',
'PRESTIGE.NS',
'APARINDS.NS',
'COHANCE.NS',
'MAHSCOOTER.NS',
'RELINFRA.NS',
'CUB.NS',
'GVT&D.NS',
'SIGNATURE.NS',
'TEJASNET.NS',
'JTLIND.NS',
'PVP.NS'
    ]
    
    ANALYSIS_DIR = Path(__file__).parent / 'nifty50_analysis'
    FUNDAMENTAL_DATA_DIR = Path(__file__).parent / 'data' / 'fundamentals'
    PRICE_DATA_DIR = Path(__file__).parent / 'data' / 'prices'
    
    # Analysis parameters
    DAYS_LOOKBACK = 420  # Enough calendar days for 200+ trading bars
    MIN_DATA_POINTS = 200  # Minimum bars required for SMA-200/long-term trend analysis
    
    # Sector classification for enhanced analysis
    SECTOR_MAPPING = {
        'IT': StockCategory.TECH_IT,
        'TECH': StockCategory.TECH_IT,
        'TCS': StockCategory.TECH_IT,
        'INFY': StockCategory.TECH_IT,
        'WIPRO': StockCategory.TECH_IT,
        'PSU': StockCategory.PSU_GOVERNMENT,
        'COAL': StockCategory.PSU_GOVERNMENT,
        'POWER': StockCategory.PSU_GOVERNMENT,
        'FMCG': StockCategory.FMCG_CONSUMER,
        'CONSUMER': StockCategory.FMCG_CONSUMER,
        'FINANCIAL': StockCategory.FINANCIALS,
        'BANK': StockCategory.FINANCIALS,
        'INSURANCE': StockCategory.FINANCIALS,
        'ENERGY': StockCategory.ENERGY,
        'OIL': StockCategory.ENERGY,
    }


# ============================================================================
# SETUP LOGGING
# ============================================================================

def setup_logging():
    """Configure logging with file and console output"""
    Config.ANALYSIS_DIR.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = Config.ANALYSIS_DIR / f'INTEGRATED_ANALYSIS_{timestamp}.txt'
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger, log_file


logger, log_file = setup_logging()


# ============================================================================
# DATA FETCHING & PREPARATION
# ============================================================================

class IntegratedDataFetcher:
    """Fetch price and fundamental data for analysis"""
    
    def __init__(self, logger):
        self.logger = logger
        self.price_cache = {}  # In-memory cache for price data
        self.fundamental_cache = {}  # In-memory cache for fundamental data
    
    def fetch_price_data(self, ticker, days=None):
        """Fetch OHLCV data from yfinance (or return from cache)"""
        try:
            if days is None:
                days = Config.DAYS_LOOKBACK
            # Return from cache if available
            if ticker in self.price_cache:
                return self.price_cache[ticker]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            self.logger.debug(f"Fetching price data for {ticker}...")
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if data.empty or len(data) < Config.MIN_DATA_POINTS:
                self.logger.warning(f"{ticker}: Insufficient data ({len(data)} bars)")
                return None
            
            # Ensure ascending order and clean any NaN
            data = data.sort_index()
            data = data.dropna()
            
            # Cache it
            self.price_cache[ticker] = data
            
            return data
        except Exception as e:
            self.logger.error(f"{ticker}: Price fetch failed - {str(e)[:50]}")
            return None
    
    def bulk_fetch_all_price_data(self, tickers, days=None):
        """
        PHASE 1: Bulk fetch ALL price data synchronously (sequential)
        This ensures latest data before any analysis
        """
        if days is None:
            days = Config.DAYS_LOOKBACK
        self.logger.info("="*70)
        self.logger.info("PHASE 1: BULK DATA COLLECTION - STARTING")
        self.logger.info("="*70)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        successful = 0
        failed = 0
        
        for i, ticker in enumerate(tickers, 1):
            try:
                self.logger.info(f"[{i}/{len(tickers)}] Fetching: {ticker}")
                
                # Sequential/synchronous download (yfinance friendly)
                data = yf.download(ticker, start=start_date, end=end_date, progress=False)
                
                if data.empty or len(data) < Config.MIN_DATA_POINTS:
                    self.logger.warning(f"{ticker}: Insufficient data ({len(data)} bars) - SKIPPING")
                    failed += 1
                    continue
                
                # Handle MultiIndex columns from yfinance (when single ticker, columns are still MultiIndex)
                if isinstance(data.columns, pd.MultiIndex):
                    # Flatten MultiIndex: ('Close', 'TICKER') -> 'Close'
                    data.columns = data.columns.get_level_values(0)
                
                # Ensure ascending order and clean any NaN
                data = data.sort_index()
                data = data.dropna()
                
                # Cache it
                self.price_cache[ticker] = data
                self.logger.debug(f"{ticker}: Cached {len(data)} bars of price data")
                successful += 1
                
            except Exception as e:
                self.logger.error(f"{ticker}: Download failed - {str(e)[:60]} - SKIPPING")
                failed += 1
                continue
        
        self.logger.info("="*70)
        self.logger.info(f"PHASE 1 COMPLETE: {successful} successful, {failed} failed")
        self.logger.info(f"Total tickers with valid data: {len(self.price_cache)}")
        self.logger.info("="*70)
        
        return self.price_cache
    
    def bulk_fetch_all_fundamental_data(self, tickers):
        """
        Bulk fetch fundamental data for all tickers
        """
        self.logger.info("="*70)
        self.logger.info("PHASE 1B: BULK FUNDAMENTAL DATA COLLECTION - STARTING")
        self.logger.info("="*70)
        
        for i, ticker in enumerate(tickers, 1):
            try:
                if ticker not in self.price_cache:
                    self.logger.debug(f"{ticker}: Skipped (no price data)")
                    continue
                
                fundamentals = self.load_fundamental_data(ticker)
                if fundamentals:
                    self.fundamental_cache[ticker] = fundamentals
                    self.logger.debug(f"{ticker}: Cached fundamental data")
                
            except Exception as e:
                self.logger.debug(f"{ticker}: Fundamental data fetch failed - {str(e)[:40]}")
                continue
        
        self.logger.info("="*70)
        self.logger.info(f"PHASE 1B COMPLETE: {len(self.fundamental_cache)} tickers with fundamental data")
        self.logger.info("="*70)
    
    def get_market_index_data(self, days=None):
        """Fetch market index (NIFTY50 proxy) for regime analysis"""
        try:
            if days is None:
                days = Config.DAYS_LOOKBACK
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = yf.download('^NSEI', start=start_date, end=end_date, progress=False)
            
            if data.empty or len(data) < Config.MIN_DATA_POINTS:
                self.logger.warning(f"Market index: Insufficient data ({len(data)} bars)")
                return None
            
            return data.sort_index().dropna()
        except Exception as e:
            self.logger.error(f"Market index fetch failed: {str(e)[:50]}")
            return None
    
    def load_fundamental_data(self, ticker):
        """Load fundamental data from CSV files in data/fundamentals/"""
        # Sector mapping for Indian stocks
        SECTOR_MAP = {
            # Technology
            'TCS': 'Technology', 'INFY': 'Technology', 'WIPRO': 'Technology', 'HCLTECH': 'Technology',
            'TECHM': 'Technology', 'LTI': 'Technology', 'COFORGE': 'Technology', 'PERSISTENT': 'Technology',
            # Financials/Banks
            'HDFC': 'Financial Services', 'HDFCBANK': 'Financial Services', 'ICICIBANK': 'Financial Services',
            'SBIN': 'Financial Services', 'AXISBANK': 'Financial Services', 'KOTAKBANK': 'Financial Services',
            'BANKBARODA': 'Financial Services', 'PNB': 'Financial Services', 'INDUSINDBK': 'Financial Services',
            'BAJAJFINSV': 'Financial Services', 'BAJFINANCE': 'Financial Services', 'SBILIFE': 'Financial Services',
            'HDFCLIFE': 'Financial Services', 'ICICIGI': 'Financial Services',
            # PSU / Government
            'NTPC': 'PSU', 'POWERGRID': 'PSU', 'COALINDIA': 'PSU', 'ONGC': 'PSU', 'IOCL': 'PSU',
            'GAIL': 'PSU', 'SAIL': 'PSU', 'NMDC': 'PSU', 'BHEL': 'PSU', 'BEL': 'PSU',
            # Energy / Oil & Gas
            'RELIANCE': 'Energy', 'BPCL': 'Energy', 'HINDPETRO': 'Energy', 'ADANIPOWER': 'Energy',
            'TATAPOWER': 'Energy',
            # FMCG / Consumer
            'HINDUNILVR': 'FMCG', 'ITC': 'FMCG', 'NESTLEIND': 'FMCG', 'BRITANNIA': 'FMCG',
            'DABUR': 'FMCG', 'MARICO': 'FMCG', 'GODREJCP': 'FMCG', 'COLPAL': 'FMCG',
            'TATACONSUM': 'FMCG', 'VBL': 'FMCG',
            # Auto
            'MARUTI': 'Automobile', 'TATAMOTORS': 'Automobile', 'M&M': 'Automobile', 'BAJAJ-AUTO': 'Automobile',
            'HEROMOTOCO': 'Automobile', 'EICHERMOT': 'Automobile', 'ASHOKLEY': 'Automobile',
            # Pharma
            'SUNPHARMA': 'Pharmaceuticals', 'DRREDDY': 'Pharmaceuticals', 'CIPLA': 'Pharmaceuticals',
            'AUROPHARMA': 'Pharmaceuticals', 'DIVISLAB': 'Pharmaceuticals',
            # Metals / Materials
            'TATASTEEL': 'Materials', 'JSWSTEEL': 'Materials', 'HINDALCO': 'Materials',
            'VEDL': 'Materials', 'COALINDIA': 'Materials',
            # Cement
            'ULTRACEMCO': 'Cement', 'GRASIM': 'Cement', 'AMBUJACEM': 'Cement', 'ACC': 'Cement',
            # Telecom
            'BHARTIARTL': 'Telecom',
        }
        
        try:
            # Try to load from CSV file first
            csv_file = Config.FUNDAMENTAL_DATA_DIR / f"{ticker}.csv"
            
            if csv_file.exists():
                # Read CSV file
                df = pd.read_csv(csv_file)
                
                if df.empty:
                    self.logger.warning(f"{ticker}: CSV file is empty")
                    return None
                
                # Get the most recent row (latest date)
                latest = df.iloc[0]  # First row should be most recent
                
                # Determine sector from ticker
                base_symbol = ticker.split('.')[0]  # Remove .NS suffix
                sector = SECTOR_MAP.get(base_symbol, 'Industrials')  # Default to Industrials
                
                # Extract fundamental metrics from CSV
                fundamentals = {
                    'pe_ratio': float(latest.get('pe_ratio', 20.0)),
                    'pb_ratio': float(latest.get('pb_ratio', 1.5)),
                    'roe': float(latest.get('roe', 15.0)),
                    'roce': float(latest.get('roce', 15.0)),
                    'debt_to_equity': float(latest.get('debt_to_equity', 0.5)),
                    'current_ratio': 1.5,  # Not in CSV, use default
                    'revenue_cagr_5yr': float(latest.get('revenue_cagr', 10.0)),
                    'eps_cagr_5yr': float(latest.get('revenue_cagr', 10.0)),  # Use revenue as proxy
                    'profit_cagr_5yr': float(latest.get('profit_cagr', 10.0)),
                    'net_profit_margin': 10.0,  # Not in CSV, use default
                    'dividend_yield': float(latest.get('dividend_yield', 2.0)),
                    'pe_percentile': 50.0,  # Not in CSV, use default
                    'debt_service_coverage': 2.0,  # Not in CSV, use default
                    'sector': sector,
                }
                
                self.logger.debug(f"{ticker}: Loaded fundamentals from CSV (ROE={fundamentals['roe']:.1f}%, ROCE={fundamentals['roce']:.1f}%, Sector={sector})")
                return fundamentals
            
            # Fallback to yfinance if CSV doesn't exist
            self.logger.warning(f"{ticker}: CSV file not found, fetching from yfinance")
            stock = yf.Ticker(ticker)
            info = stock.info
            
            fundamentals = {
                'pe_ratio': info.get('trailingPE', 20),
                'pb_ratio': info.get('priceToBook', 1.5),
                'roe': info.get('returnOnEquity', 0.15) * 100 if info.get('returnOnEquity') else 15.0,
                'roce': info.get('returnOnCapital', 0.15) * 100 if info.get('returnOnCapital') else 15.0,
                'debt_to_equity': info.get('debtToEquity', 0.5) / 100 if info.get('debtToEquity') else 0.5,
                'current_ratio': info.get('currentRatio', 1.5),
                'revenue_cagr_5yr': 10.0,  # Default
                'eps_cagr_5yr': 10.0,  # Default
                'profit_cagr_5yr': 10.0,  # Default
                'net_profit_margin': info.get('profitMargins', 0.10) * 100 if info.get('profitMargins') else 10.0,
                'dividend_yield': info.get('dividendYield', 0.02) * 100 if info.get('dividendYield') else 2.0,
                'pe_percentile': 50.0,  # Default
                'debt_service_coverage': 2.0,  # Default
                'sector': info.get('sector', 'Unknown'),
            }
            
            self.logger.debug(f"{ticker}: Fetched fundamentals from yfinance (fallback)")
            return fundamentals
            
        except Exception as e:
            self.logger.error(f"{ticker}: Fundamental data load failed - {str(e)[:100]}")
            return None


# ============================================================================
# INTEGRATED ANALYSIS ENGINE
# ============================================================================

class IntegratedAnalysisEngine:
    """
    Main engine that orchestrates all 21 analysis modules
    Uses RefactoredDecisionEngine as the primary orchestrator
    """
    
    def __init__(self, logger, market_index_data):
        self.logger = logger
        self.market_index_data = market_index_data
        self.data_fetcher = IntegratedDataFetcher(logger)
        
        # Initialize all 21 modules
        try:
            # Core analysis engines (Modules 1-5)
            self.tech_analyzer = TechnicalAnalyzer()
            self.fund_analyzer = FundamentalAnalyzer()
            self.analysis_engine = StockAnalysisEngine()
            self.decision_engine = DecisionEngine()
            self.stock_classifier = StockClassifier()
            
            # Enhanced analyzers (Modules 6-7)
            self.enhanced_fund_analyzer = EnhancedFundamentalAnalyzer()
            self.enhanced_tech_analyzer = EnhancedTechnicalAnalyzer()
            
            # Risk and filter modules (Modules 8-11)
            self.regime_filter = MarketRegimeFilter()
            self.event_analyzer = EventRiskAnalyzer()
            self.convergence_detector = ConvergenceDetector()
            self.vol_scorer = VolatilityAdjustedScoring()
            
            # Drawdown and confidence modules (Modules 12-13)
            self.drawdown_modeler = DrawdownModeler()
            self.confidence_quantifier = ConfidenceQuantifier()
            
            # Data confidence and decision modules (Modules 14-16)
            self.data_confidence_detector = DataConfidenceDetector()
            self.confidence_cap_engine = ConfidenceCapEngine()
            self.uncertainty_decision = UncertaintyAwareDecisionEngine()
            
            # Output and orchestration (Modules 17-18)
            self.output_formatter = TwoLayerOutputFormatter()
            self.refactored_decision_engine = RefactoredDecisionEngine()
            
            # Diagnostics (Module 19)
            self.diagnostics = DiagnosticsCollector()
            
            self.logger.info("✓ All 21 modules initialized successfully")
        except Exception as e:
            self.logger.error(f"Module initialization failed: {e}")
            raise
    
    def analyze_stock(self, ticker):
        """
        PIPELINE: Complete integrated analysis using all 21 modules
        
        Flow:
        1. Fetch price + fundamental data
        2. Classify stock type (Module: StockClassifier)
        3. Detect market regime (Module: MarketRegimeFilter)
        4. Analyze fundamentals - Enhanced (Module: EnhancedFundamentalAnalyzer)
        5. Analyze technicals - Enhanced (Module: EnhancedTechnicalAnalyzer)
        6. Analyze event risk (Module: EventRiskAnalyzer)
        7. Detect convergence (Module: ConvergenceDetector)
        8. Score volatility-adjusted (Module: VolatilityAdjustedScorer)
        9. Model drawdown (Module: DrawdownModeler)
        10. Quantify confidence (Module: ConfidenceQuantifier)
        11. Detect data confidence state (Module: DataConfidenceDetector)
        12. Cap confidence (Module: ConfidenceCapEngine)
        13. Apply uncertainty constraints (Module: UncertaintyAwareDecision)
        14. Orchestrate final decision (Module: RefactoredDecisionEngine)
        15. Format output (Module: TwoLayerOutputFormatter)
        
        Returns: Comprehensive two-layer output (investment view + trade setup)
        """
        try:
            self.logger.info(f"PHASE 2: {ticker} - Analyzing with all 21 modules")
            
            # ================================================================
            # STEP 0: FETCH DATA (Modules: TechnicalAnalyzer, FundamentalAnalyzer, AnalysisEngine)
            # ================================================================
            
            # Get price data from cache
            price_data = self.data_fetcher.price_cache.get(ticker)
            if price_data is None or price_data.empty:
                self.logger.warning(f"{ticker}: No cached price data available")
                return None
            
            # Get fundamental data from cache
            fundamental_data = self.data_fetcher.fundamental_cache.get(ticker, {})
            if not fundamental_data:
                self.logger.warning(f"{ticker}: No cached fundamental data")
                return None
            
            # Extract key metrics
            current_price = float(price_data['Close'].iloc[-1])
            if pd.isna(current_price) or not np.isfinite(current_price) or current_price <= 0:
                self.logger.warning(f"{ticker}: Invalid price data")
                return None
            
            # Build FundamentalMetrics object (Module: data_models)
            fund_metrics = FundamentalMetrics(
                net_profit_margin=fundamental_data.get('net_profit_margin', 10.0),
                roe=fundamental_data.get('roe', 15.0),
                roce=fundamental_data.get('roce', 15.0),
                revenue_cagr_5yr=fundamental_data.get('revenue_cagr_5yr', 10.0),
                eps_cagr_5yr=fundamental_data.get('eps_cagr_5yr', 10.0),
                profit_cagr_5yr=fundamental_data.get('profit_cagr_5yr', 10.0),
                debt_to_equity=fundamental_data.get('debt_to_equity', 0.5),
                current_ratio=fundamental_data.get('current_ratio', 1.5),
                debt_service_coverage=fundamental_data.get('debt_service_coverage', 2.0),
                pe_ratio=fundamental_data.get('pe_ratio', 20.0),
                pb_ratio=fundamental_data.get('pb_ratio', 1.5),
                dividend_yield=fundamental_data.get('dividend_yield', 2.0),
                pe_percentile=fundamental_data.get('pe_percentile', 50.0),
            )
            
            # Build TechnicalMetrics object (Module: data_models)
            ma20 = float(price_data['Close'].rolling(20).mean().iloc[-1]) if len(price_data) >= 20 else current_price
            ma50 = float(price_data['Close'].rolling(50).mean().iloc[-1]) if len(price_data) >= 50 else current_price
            ma200 = float(price_data['Close'].rolling(200).mean().iloc[-1]) if len(price_data) >= 200 else current_price
            
            # Calculate 52-week high/low
            high_52w = price_data['Close'].max() if len(price_data) > 0 else current_price
            low_52w = price_data['Close'].min() if len(price_data) > 0 else current_price
            avg_52w = (high_52w + low_52w) / 2
            
            # Calculate volume metrics
            avg_volume = float(price_data['Volume'].rolling(20).mean().iloc[-1]) if 'Volume' in price_data.columns and len(price_data) >= 20 else 1000
            current_volume = int(price_data['Volume'].iloc[-1]) if 'Volume' in price_data.columns else 1000
            volume_trend = 'increasing' if current_volume > avg_volume else 'stable'
            
            tech_metrics = TechnicalMetrics(
                current_price=current_price,
                price_52w_high=high_52w,
                price_52w_low=low_52w,
                price_52w_avg=avg_52w,
                sma_20=ma20,
                sma_200=ma200,
                rsi_14=self._calculate_rsi(price_data['Close'], 14),
                macd_line=self._calculate_macd(price_data['Close'])[0],
                macd_signal=self._calculate_macd(price_data['Close'])[1],
                macd_histogram=self._calculate_macd(price_data['Close'])[2],
                atr_14=self._calculate_atr(price_data['High'], price_data['Low'], price_data['Close'], 14),
                avg_volume_20d=int(avg_volume),
                current_volume=current_volume,
                volume_trend=volume_trend,
            )
            
            # ================================================================
            # STEP 1: CLASSIFY STOCK (Module: StockClassifier)
            # ================================================================
            stock_type = self.stock_classifier.classify(
                symbol=ticker,
                fundamental_trend=fundamental_data.get('trend', 'stable'),
                fund_score=fundamental_data.get('score', 50)
            )
            self.logger.debug(f"{ticker}: Stock classified as {stock_type}")
            
            # ================================================================
            # STEP 2: MARKET REGIME DETECTION (Module: MarketRegimeFilter)
            # ================================================================
            # Calculate market index ATR if available
            if self.market_index_data is not None and len(self.market_index_data) > 0:
                index_closes = self.market_index_data['Close'].values.tolist()
                # DEBUG: Check what we have
                if isinstance(index_closes[-1], (list, tuple)):
                    # If it's somehow nested, flatten it
                    index_closes = [x[0] if isinstance(x, (list, tuple)) else x for x in index_closes]
                
                # Calculate ATR using pandas on the full data
                index_atr_single = self._calculate_atr(
                    self.market_index_data['High'],
                    self.market_index_data['Low'],
                    self.market_index_data['Close'],
                    14
                )
                index_atr_values = [index_atr_single] * len(index_closes)  # Broadcast current ATR
                market_breadth = {'advances': 250, 'declines': 250}  # Balanced market assumption
                current_index_price = float(index_closes[-1])
                current_index_atr = index_atr_single
            else:
                index_closes = [current_price]
                index_atr_values = [1.0]
                market_breadth = {'advances': 1, 'declines': 1}
                current_index_price = current_price
                current_index_atr = 1.0
            
            market_regime = self.regime_filter.analyze(
                index_prices=index_closes,
                index_atr_values=index_atr_values,
                market_breadth=market_breadth,
                current_price=current_index_price,
                current_atr=current_index_atr
            )
            self.logger.debug(f"{ticker}: Market regime = {market_regime.regime_type.value if hasattr(market_regime, 'regime_type') else 'UNKNOWN'}")
            
            # ================================================================
            # STEP 3: ENHANCED FUNDAMENTAL ANALYSIS (Module: EnhancedFundamentalAnalyzer)
            # ================================================================
            # Determine stock category using sector data from fundamentals
            sector = fundamental_data.get('sector', ticker.split('.')[0]).upper()
            
            # Map sector to StockCategory
            if stock_type == 'psu_government' or 'POWER' in sector or 'COAL' in sector or 'NTPC' in sector:
                stock_cat = StockCategory.PSU_GOVERNMENT
            elif 'TECH' in sector or 'IT' in sector or ticker in ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS']:
                stock_cat = StockCategory.TECH_IT
            elif 'FMCG' in sector or 'CONSUMER' in sector or ticker in ['HINDUNILVR.NS', 'NESTLEIND.NS', 'BRITANNIA.NS']:
                stock_cat = StockCategory.FMCG_CONSUMER
            elif 'BANK' in sector or 'FINANC' in sector or ticker in ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS']:
                stock_cat = StockCategory.FINANCIALS
            elif 'ENERGY' in sector or 'OIL' in sector or ticker in ['RELIANCE.NS', 'ONGC.NS', 'BPCL.NS']:
                stock_cat = StockCategory.ENERGY
            elif stock_type == 'recovery_turnaround':
                stock_cat = StockCategory.INDUSTRIALS
            else:
                # Default based on common patterns
                stock_cat = StockCategory.TECH_IT
            
            enhanced_fund_analysis = self.enhanced_fund_analyzer.analyze(
                symbol=ticker,
                category=stock_cat,
                pe_ratio=fund_metrics.pe_ratio,
                peg_ratio=2.0,  # Estimated
                roe=fund_metrics.roe,
                roce=fund_metrics.roce,
                debt_equity=fund_metrics.debt_to_equity,
                current_ratio=fund_metrics.current_ratio,
                profit_margin=fund_metrics.net_profit_margin,
                revenue_growth=fund_metrics.revenue_cagr_5yr,
                fcf=100000.0,  # Placeholder
                npa_ratio=0.0,
                dividend_yield=fund_metrics.dividend_yield
            )
            self.logger.debug(f"{ticker}: Fundamental score = {enhanced_fund_analysis.overall_score if hasattr(enhanced_fund_analysis, 'overall_score') else 'N/A'}")
            
            # ================================================================
            # STEP 4: ENHANCED TECHNICAL ANALYSIS (Module: EnhancedTechnicalAnalyzer)
            # ================================================================
            recent_high_20d = price_data['High'].tail(20).max() if len(price_data) >= 20 else current_price
            recent_low_20d = price_data['Low'].tail(20).min() if len(price_data) >= 20 else current_price
            ema_50 = float(price_data['Close'].ewm(span=50).mean().iloc[-1]) if len(price_data) >= 50 else current_price
            vwap_val = current_price  # Placeholder
            
            enhanced_tech_analysis = self.enhanced_tech_analyzer.analyze(
                current_price=current_price,
                ema_20=ma20,
                ema_50=ema_50,
                ema_200=ma200,
                atr=tech_metrics.atr_14,
                rsi_14=tech_metrics.rsi_14,
                macd_line=tech_metrics.macd_line,
                macd_signal=tech_metrics.macd_signal,
                volume_current=float(current_volume),
                volume_20ma=float(avg_volume),
                recent_high_20d=recent_high_20d,
                recent_low_20d=recent_low_20d,
                recent_high_52w=high_52w,
                recent_low_52w=low_52w,
                vwap=vwap_val,
                htf_trend='uptrend' if current_price > ma200 else 'downtrend'
            )
            self.logger.debug(f"{ticker}: Technical setup type = {enhanced_tech_analysis.setup_type if hasattr(enhanced_tech_analysis, 'setup_type') else 'UNKNOWN'}")
            
            # ================================================================
            # STEP 5: EVENT RISK ANALYSIS (Module: EventRiskAnalyzer)
            # ================================================================
            event_risk = self.event_analyzer.check_event_proximity(
                symbol=ticker,
                current_date=datetime.now(),
                earnings_date=fundamental_data.get('next_earnings_date'),
                dividend_date=fundamental_data.get('dividend_ex_date'),
                other_events=None
            )
            self.logger.debug(f"{ticker}: Event risk level = {event_risk.risk_level if hasattr(event_risk, 'risk_level') else 'UNKNOWN'}")
            
            # ================================================================
            # STEP 6: CONVERGENCE DETECTION (Module: ConvergenceDetector)
            # ================================================================
            # Map tech_analysis to a score (confidence: BUY=80, WAIT=50, NO TRADE=20)
            tech_score_map = {'BUY': 80, 'WAIT': 50, 'NO TRADE': 20}
            tech_score = tech_score_map.get(enhanced_tech_analysis.confidence, 50)
            
            convergence = self.convergence_detector.detect_convergence(
                symbol=ticker,
                stock_type=stock_type,
                fund_score=enhanced_fund_analysis.overall_score,
                fundamental_trend='bullish' if enhanced_fund_analysis.overall_score > 60 else 'bearish',
                tech_score=tech_score,
                momentum_score=self._calculate_momentum_score(price_data['Close']),
                rsi=tech_metrics.rsi_14,
                macd_histogram=tech_metrics.macd_histogram,
                volume_trend='increasing' if price_data['Volume'].iloc[-1] > price_data['Volume'].rolling(20).mean().iloc[-1] else 'stable'
            )
            self.logger.debug(f"{ticker}: Convergence detected = {convergence.get('convergence_detected', False)}")
            
            # ================================================================
            # STEP 7: VOLATILITY-ADJUSTED SCORING (Module: VolatilityAdjustedScoring)
            # ================================================================
            vol_adjustment = self.vol_scorer.adjust_tech_score(
                base_tech_score=tech_score,
                stock_type=stock_type,
                rsi=tech_metrics.rsi_14,
                atr_percent=(tech_metrics.atr_14 / current_price * 100) if current_price > 0 else 0,
                price_vs_ma20=((current_price - ma20) / ma20 * 100) if ma20 > 0 else 0,
                volume_trend='increasing'
            )
            self.logger.debug(f"{ticker}: Volatility-adjusted score = {vol_adjustment.get('adjusted_score', 50)}")
            
            # ================================================================
            # STEP 8: DRAWDOWN MODELING (Module: DrawdownModeler)
            # ================================================================
            drawdown_analysis = self.drawdown_modeler.analyze_setup_fragility(
                setup_type=str(enhanced_tech_analysis.setup_type.name) if enhanced_tech_analysis.setup_type else 'TREND_CONTINUATION',
                sector=fundamental_data.get('sector', 'OTHER'),
                entry_price=current_price,
                proposed_stop=current_price * 0.95,
                current_atr=tech_metrics.atr_14,
                baseline_atr=tech_metrics.atr_14
            )
            drawdown_fragility = drawdown_analysis.get('fragility_level', 'UNKNOWN') if isinstance(drawdown_analysis, dict) else getattr(drawdown_analysis, 'fragility_level', 'UNKNOWN')
            self.logger.debug(f"{ticker}: Drawdown fragility = {drawdown_fragility}")
            
            # ================================================================
            # STEP 9: CONFIDENCE QUANTIFICATION (Module: ConfidenceQuantifier)
            # ================================================================
            # Extract setup type from trade setup
            setup_type_obj = enhanced_tech_analysis.setup_type if enhanced_tech_analysis.setup_type else ConfSetupType.NO_SETUP
            
            # Derive other parameters needed for quantify
            sector_map = {
                'TECH_IT': 'tech',
                'PSU_GOVERNMENT': 'psu',
                'FMCG_CONSUMER': 'fmcg',
                'FINANCIALS': 'finance',
                'ENERGY': 'energy',
                'INDUSTRIALS': 'industrial',
                'PHARMA': 'pharma',
                'AUTOS': 'auto'
            }
            sector = sector_map.get(stock_cat.name, 'general')
            volatility_regime = 'high' if tech_metrics.atr_14 > current_price * 0.05 else 'normal'
            
            # Count structural signals
            structure_signals = 0
            if enhanced_tech_analysis.confidence == 'BUY':
                structure_signals = 3
            elif enhanced_tech_analysis.confidence == 'WAIT':
                structure_signals = 1
            
            confidence_metrics = self.confidence_quantifier.quantify(
                setup_type=setup_type_obj,
                sector=sector,
                volatility_regime=volatility_regime,
                fund_score=enhanced_fund_analysis.overall_score,
                tech_score=tech_score,
                rr_ratio=2.0,  # Placeholder
                structure_signals=structure_signals,
                breakout_confirmed=enhanced_tech_analysis.confidence == 'BUY',
                thesis_clear=enhanced_fund_analysis.overall_score > 50,
                invalidation_defined=True,
                current_price_in_zone=enhanced_tech_analysis.buy_zone_low is not None and current_price >= enhanced_tech_analysis.buy_zone_low if enhanced_tech_analysis.buy_zone_low else False,
                volume_confirmed=volume_trend == 'increasing'
            )
            conf_score = confidence_metrics.total_confidence if hasattr(confidence_metrics, 'total_confidence') else 50
            self.logger.debug(f"{ticker}: Raw confidence = {conf_score}")
            
            # ================================================================
            # STEP 10: DATA CONFIDENCE DETECTION (Module: DataConfidenceDetector)
            # ================================================================
            regime_type = market_regime.get('regime_type', 'TRENDING') if isinstance(market_regime, dict) else 'TRENDING'
            regime_strength = market_regime.get('regime_strength', 0.5) if isinstance(market_regime, dict) else 0.5
            
            data_confidence_state, cap_reason_detect = self.data_confidence_detector.detect_state(
                fundamental_data=fundamental_data,
                technical_data={'Close': price_data['Close'].values, 'Volume': price_data['Volume'].values if 'Volume' in price_data.columns else None},
                regime_data={'type': str(regime_type), 'strength': regime_strength}
            )
            self.logger.debug(f"{ticker}: Data confidence state = {data_confidence_state}")
            
            # ================================================================
            # STEP 11: CONFIDENCE CAPPING (Module: ConfidenceCapEngine)
            # ================================================================
            capped_confidence, cap_value, cap_reason = self.confidence_cap_engine.cap_confidence(
                raw_confidence=conf_score,
                data_state=data_confidence_state
            )
            self.logger.debug(f"{ticker}: Capped confidence = {capped_confidence} (reason: {cap_reason})")
            
            # ================================================================
            # STEP 12: UNCERTAINTY-AWARE DECISION (Module: UncertaintyAwareDecisionEngine)
            # ================================================================
            raw_decision = self._make_raw_decision(
                enhanced_fund_analysis, enhanced_tech_analysis, 
                market_regime, conf_score
            )
            
            uncertainty_decision = self.uncertainty_decision.make_uncertainty_aware_decision(
                raw_decision=raw_decision,
                raw_confidence=confidence_metrics.total_confidence,
                data_confidence_state=data_confidence_state,
                final_confidence=capped_confidence,
                cap_details={'reason': cap_reason, 'cap_value': cap_value}
            )
            self.logger.debug(f"{ticker}: Final decision after uncertainty = {uncertainty_decision.get('decision', raw_decision)}")
            
            # ================================================================
            # STEP 13: ORCHESTRATE FINAL DECISION (Module: RefactoredDecisionEngine)
            # ================================================================
            # Use refactored decision engine with all individual parameters
            investment_view, trade_setup, confidence_report, formatted_op = self.refactored_decision_engine.analyze_stock(
                symbol=ticker,
                name=ticker.replace('.NS', ''),
                sector=fundamental_data.get('sector', 'UNKNOWN'),
                category=stock_cat,
                analysis_date=datetime.now(),
                pe_ratio=fund_metrics.pe_ratio,
                peg_ratio=2.0,
                roe=fund_metrics.roe,
                roce=fund_metrics.roce,
                debt_equity=fund_metrics.debt_to_equity,
                current_ratio=fund_metrics.current_ratio,
                profit_margin=fund_metrics.net_profit_margin,
                revenue_growth=fund_metrics.revenue_cagr_5yr,
                fcf=100000.0,
                current_price=current_price,
                ema_20=ma20,
                ema_50=ema_50,
                ema_200=ma200,
                atr=tech_metrics.atr_14,
                rsi_14=tech_metrics.rsi_14,
                macd_line=tech_metrics.macd_line,
                macd_signal=tech_metrics.macd_signal,
                volume_current=float(current_volume),
                volume_20ma=float(avg_volume),
                recent_high_20d=recent_high_20d,
                recent_low_20d=recent_low_20d,
                recent_high_52w=high_52w,
                recent_low_52w=low_52w,
                npa_ratio=0.0,
                dividend_yield=fund_metrics.dividend_yield,
                vwap=current_price,
                htf_trend='uptrend' if current_price > ma200 else 'downtrend'
            )
            self.logger.debug(f"{ticker}: Investment decision = {investment_view.decision if hasattr(investment_view, 'decision') else 'N/A'}")
            
            # ================================================================
            # STEP 14: FORMAT OUTPUT (Module: TwoLayerOutputFormatter)
            # ================================================================
            formatted_output = self.output_formatter.format_report(
                symbol=ticker,
                investment_view=investment_view,
                trade_setup=trade_setup,
                confidence=confidence_report
            )
            
            # ================================================================
            # STEP 15: COLLECT DIAGNOSTICS (Module: DiagnosticsCollector)
            # ================================================================
            self.diagnostics.record_fundamental_score(
                score=enhanced_fund_analysis.overall_score,
                sector=fundamental_data.get('sector', 'UNKNOWN'),
                validity='VALID' if getattr(enhanced_fund_analysis, 'validity', 'VALID') == 'VALID' else 'WEAK'
            )
            
            # Add investment view decision to diagnostics
            if str(investment_view.decision) == 'ACCUMULATE':
                self.diagnostics.buy_signals += 1
            elif str(investment_view.decision) == 'HOLD':
                self.diagnostics.hold_signals += 1
            else:
                self.diagnostics.sell_signals += 1
            
            self.logger.info(f"[✓ DONE] {ticker} analysis complete - Signal: {investment_view.decision}")
            
            # Return both formatted text and structured data
            return {
                'formatted_report': formatted_output,
                'ticker': ticker,
                'current_price': current_price,
                'decision': str(investment_view.decision),
                'target_price': getattr(trade_setup, 'target_price', 0),
                'stop_loss': getattr(trade_setup, 'stop_loss', 0),
                'scores': {
                    'fundamental_score': enhanced_fund_analysis.overall_score,
                    'technical_score': confidence_report.total_score,
                    'confidence': confidence_report.total_score
                }
            }
            
        except Exception as e:
            self.logger.error(f"[ERROR] {ticker} analysis failed: {str(e)}")
            traceback.print_exc()
            return None
            regime = self._detect_market_regime()
            self.logger.debug(f"{ticker}: Market regime = {regime['type']}")
            
            # Step 3: Enhanced technical analysis
            tech_analysis = self._analyze_technical(ticker, price_data)
            
            # Step 4: Enhanced fundamental analysis
            fund_analysis = self._analyze_fundamental(ticker)
            
            # Step 5: Event risk analysis
            event_risk = self._analyze_event_risk(ticker)
            
            # Step 6: Convergence detection
            convergence = self._detect_convergence(ticker, price_data)
            
            # Step 7: Volatility-adjusted scoring
            vol_adjusted = self._score_volatility_adjusted(ticker, price_data)
            
            # Step 8: Drawdown modeling
            drawdown = self._model_drawdown(ticker, price_data)
            
            # Step 9: Confidence quantification
            confidence = self._quantify_confidence(
                tech_analysis, fund_analysis, event_risk, convergence
            )
            
            # Step 10: Final decision
            final_decision = self._make_final_decision(
                ticker, tech_analysis, fund_analysis, confidence, regime
            )
            
            # Step 11: Format output (two-layer)
            output = self._format_output(
                ticker, tech_analysis, fund_analysis, confidence, 
                final_decision, regime, event_risk, drawdown
            )
            
            self.logger.info(f"[DONE] {ticker} analysis complete - Signal: {output.get('signal', 'N/A')}")
            return output
            
        except Exception as e:
            self.logger.error(f"[ERROR] {ticker} analysis failed: {str(e)}")
            traceback.print_exc()
            return None
    
    # ================================================================
    # HELPER METHODS FOR CALCULATIONS
    # ================================================================
    
    def _calculate_rsi(self, close_prices, period=14):
        """Calculate RSI (Relative Strength Index)"""
        try:
            deltas = close_prices.diff()
            gains = (deltas[deltas > 0]).rolling(period).mean()
            losses = (-deltas[deltas < 0]).rolling(period).mean()
            rs = gains / (losses + 0.0001)
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if len(rsi) > 0 else 50.0
        except:
            return 50.0
    
    def _calculate_macd(self, close_prices):
        """Calculate MACD components: (line, signal, histogram)"""
        try:
            ema12 = close_prices.ewm(span=12).mean()
            ema26 = close_prices.ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9).mean()
            macd_histogram = macd_line - signal_line
            return (
                float(macd_line.iloc[-1]) if len(macd_line) > 0 else 0.0,
                float(signal_line.iloc[-1]) if len(signal_line) > 0 else 0.0,
                float(macd_histogram.iloc[-1]) if len(macd_histogram) > 0 else 0.0
            )
        except:
            return (0.0, 0.0, 0.0)
    
    def _calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range (ATR)"""
        try:
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(period).mean()
            return float(atr.iloc[-1]) if len(atr) > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_momentum_score(self, close_prices, period=10):
        """Calculate momentum score"""
        try:
            if len(close_prices) < period:
                return 50.0
            momentum = ((close_prices.iloc[-1] - close_prices.iloc[-period]) / close_prices.iloc[-period]) * 100
            # Normalize to 0-100 scale (assume +/- 5% is extreme)
            score = 50 + (momentum / 5) * 50
            return max(0, min(100, float(score)))
        except:
            return 50.0
    
    def _make_raw_decision(self, fund_analysis, tech_analysis, market_regime, confidence):
        """Make raw decision before uncertainty adjustment"""
        try:
            # Check fundamental validity
            if fund_analysis.validity == 'INVALID':
                return 'AVOID'
            
            # Check market regime
            if market_regime.regime_type == MarketRegimeType.RISK_OFF:
                return 'HOLD'
            
            # Check technical setup
            if tech_analysis.setup_type == TechSetupType.NO_TRADE:
                return 'HOLD'
            
            # Combine signals
            if fund_analysis.validity == 'VALID' and tech_analysis.setup_type != TechSetupType.NO_TRADE and confidence > 60:
                return 'BUY'
            elif fund_analysis.validity == 'WEAK':
                return 'HOLD'
            else:
                return 'HOLD'
        except:
            return 'HOLD'


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function with 3-phase architecture"""
    
    logger.info("="*70)
    logger.info("NIFTY50 INTEGRATED ANALYSIS - Starting")
    logger.info(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70)
    
    # Create output directory
    Config.ANALYSIS_DIR.mkdir(exist_ok=True, parents=True)
    Config.FUNDAMENTAL_DATA_DIR.mkdir(exist_ok=True, parents=True)
    Config.PRICE_DATA_DIR.mkdir(exist_ok=True, parents=True)
    
    try:
        # Initialize fetcher (shared across phases)
        fetcher = IntegratedDataFetcher(logger)
        
        # ================================================================
        # PHASE 1: BULK DATA COLLECTION (Synchronous downloads)
        # ================================================================
        logger.info("\n" + "="*70)
        logger.info("PHASE 1: BULK DATA COLLECTION - Starting")
        logger.info("="*70)
        
        # Analyze all stocks in the list
        stocks_to_analyze = Config.NIFTY50_STOCKS
        
        logger.info(f"Bulk-fetching price data for {len(stocks_to_analyze)} stocks (SYNCHRONOUS)...")
        price_cache = fetcher.bulk_fetch_all_price_data(stocks_to_analyze)
        logger.info(f"PHASE 1: Price data fetched for {len(price_cache)} stocks")
        
        logger.info(f"Bulk-fetching fundamental data for cached stocks...")
        fetcher.bulk_fetch_all_fundamental_data(stocks_to_analyze)
        logger.info(f"PHASE 1: Fundamental data fetched for {len(fetcher.fundamental_cache)} stocks")
        
        logger.info("PHASE 1: BULK DATA COLLECTION - Complete")
        logger.info("="*70 + "\n")
        
        # ================================================================
        # PHASE 2: MARKET REGIME & PRE-PROCESSING
        # ================================================================
        logger.info("PHASE 2: MARKET REGIME & PRE-PROCESSING - Starting")
        logger.info("="*70)
        
        logger.info("Fetching market index data for regime analysis...")
        market_data = fetcher.get_market_index_data()
        
        if market_data is None:
            logger.warning("Could not fetch market index - proceeding with limited regime detection")
        else:
            logger.info(f"Market index data loaded: {len(market_data)} bars")
        
        logger.info("PHASE 2: MARKET REGIME & PRE-PROCESSING - Complete")
        logger.info("="*70 + "\n")
        
        # ================================================================
        # PHASE 3: INTEGRATED ANALYSIS (Using all cached data)
        # ================================================================
        logger.info("PHASE 3: INTEGRATED ANALYSIS (21 modules) - Starting")
        logger.info("="*70)
        
        # Initialize engine
        engine = IntegratedAnalysisEngine(logger, market_data)
        # Share the cached data with engine
        engine.data_fetcher = fetcher
        
        # Analyze all stocks using cached data
        logger.info(f"Analyzing {len(stocks_to_analyze)} stocks using cached data...")
        results = []
        successful = 0
        failed = 0
        
        for i, ticker in enumerate(stocks_to_analyze, 1):
            logger.info(f"[{i}/{len(stocks_to_analyze)}] Analyzing {ticker}...")
            
            result = engine.analyze_stock(ticker)
            if result:
                results.append(result)
                successful += 1
            else:
                failed += 1
        
        logger.info("PHASE 3: INTEGRATED ANALYSIS - Complete")
        logger.info("="*70 + "\n")
        
        # ================================================================
        # OUTPUT & RESULTS
        # ================================================================
        logger.info("Saving analysis results...")
        
        # Save results
        if results:
            # Extract formatted reports for text file
            formatted_reports = [r['formatted_report'] for r in results]
            
            # Save structured JSON with prices (for dashboard)
            structured_data = [{
                'ticker': r['ticker'],
                'current_price': r['current_price'],
                'decision': r['decision'],
                'target_price': r.get('target_price', 0),
                'stop_loss': r.get('stop_loss', 0),
                'scores': r.get('scores', {})
            } for r in results]
            
            json_file = Config.ANALYSIS_DIR / f"NIFTY50_INTEGRATED_WEEKLY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_file, 'w') as f:
                json.dump(structured_data, f, indent=2, default=str, allow_nan=False)
            logger.info(f"[SUCCESS] Structured JSON results saved: {json_file}")
            
            # Save formatted text reports
            text_file = Config.ANALYSIS_DIR / f"NIFTY50_INTEGRATED_WEEKLY_{datetime.now().strftime('%Y%m%d_%H%M%S')}_REPORTS.json"
            with open(text_file, 'w') as f:
                json.dump(formatted_reports, f, indent=2, default=str, allow_nan=False)
            logger.info(f"[SUCCESS] Text reports saved: {text_file}")
            
            # CSV output
            df = pd.DataFrame(structured_data)
            csv_file = Config.ANALYSIS_DIR / f"NIFTY50_INTEGRATED_WEEKLY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(csv_file, index=False)
            logger.info(f"[SUCCESS] CSV results saved: {csv_file}")
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("ANALYSIS COMPLETE - 3-PHASE EXECUTION")
        logger.info(f"Phase 1: Bulk data collection (SYNCHRONOUS)")
        logger.info(f"Phase 2: Market regime & pre-processing")
        logger.info(f"Phase 3: Integrated analysis (21 modules)")
        logger.info(f"Results: {successful} successful, {failed} failed")
        logger.info(f"Log file: {log_file}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
