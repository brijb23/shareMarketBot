#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIFTY50 WEEKLY AUTOMATION - ENHANCED WITH MODULE-BASED ANALYSIS
Uses technical_analysis.py module for more accurate signal generation
"""

import os, json, csv, pandas as pd, numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from pathlib import Path
import traceback
import warnings
import sys

# Add src to path for proper relative imports
sys.path.insert(0, str(Path(__file__).parent))

# Import modules directly from src package
from src.technical_analysis import TechnicalAnalyzer
from src.data_models import TechnicalMetrics
from src.constants import TECHNICAL_THRESHOLDS

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Import centralized stock universe
from universes.stock_universe import get_stock_universe

# CONFIG
class Config:
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
    VOLATILITY_LOW = 12
    VOLATILITY_NORMAL = 20
    DAYS_LOOKBACK = 420  # Enough calendar days for 200+ trading bars
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / 'nifty50_analysis'
    LOG_DIR = BASE_DIR / 'logs'
    
    @classmethod
    def ensure_directories(cls):
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)

# LOGGING
def setup_logging():
    Config.ensure_directories()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = Config.LOG_DIR / f'WEEKLY_LOG_ENHANCED_{timestamp}.txt'
    logger = logging.getLogger('NIFTY50_ENHANCED')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger, log_file

# DATA COLLECTION
class DataCollector:
    REQUIRED_PRICE_COLUMNS = ['Close', 'High', 'Low', 'Volume']
    MIN_VALID_BARS = 200
    
    def __init__(self, logger):
        self.logger = logger
        self.data_cache = {}
    
    def clean_price_data(self, ticker, data):
        """Normalize downloaded OHLCV data and remove rows that cannot be analyzed."""
        if data is None or data.empty:
            self.logger.warning(f"No data for {ticker}")
            return None
        
        if isinstance(data.columns, pd.MultiIndex):
            data = data.copy()
            data.columns = data.columns.get_level_values(0)
        
        missing_cols = [col for col in self.REQUIRED_PRICE_COLUMNS if col not in data.columns]
        if missing_cols:
            self.logger.warning(f"Missing columns for {ticker}: {', '.join(missing_cols)}")
            return None
        
        original_rows = len(data)
        data = data.sort_index()
        data = data.dropna(subset=self.REQUIRED_PRICE_COLUMNS)
        
        if data.empty or len(data) < self.MIN_VALID_BARS:
            self.logger.warning(f"Insufficient valid OHLCV data for {ticker} ({len(data)} bars)")
            return None
        
        dropped_rows = original_rows - len(data)
        if dropped_rows > 0:
            self.logger.debug(f"{ticker}: Dropped {dropped_rows} rows with missing OHLCV data")
        
        return data
    
    def fetch_stock_data(self, ticker):
        try:
            self.logger.debug(f"Fetching {ticker}...")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=Config.DAYS_LOOKBACK)
            data = yf.download(ticker, start=start_date, end=end_date, progress=False, timeout=30)
            data = self.clean_price_data(ticker, data)
            if data is None:
                return None
            self.data_cache[ticker] = data
            return data
        except Exception as e:
            self.logger.error(f"Error {ticker}: {str(e)[:50]}")
            return None
    
    def fetch_all(self, stocks=None):
        if stocks is None:
            stocks = Config.NIFTY50_STOCKS
        self.logger.info(f"Fetching {len(stocks)} stocks...")
        successful = failed = 0
        for ticker in stocks:
            data = self.fetch_stock_data(ticker)
            if data is not None and not data.empty:
                successful += 1
            else:
                failed += 1
        self.logger.info(f"[OK] {successful}/{len(stocks)} stocks fetched")
        return successful, failed

# ENHANCED ANALYSIS ENGINE using technical_analysis.py module
class EnhancedAnalysisEngine:
    def __init__(self, logger):
        self.logger = logger
        self.results = []
        self.tech_analyzer = TechnicalAnalyzer()
    
    def _is_valid_number(self, value):
        return not pd.isna(value) and np.isfinite(value)
    
    def build_technical_metrics(self, ticker, data):
        """Convert raw price data to TechnicalMetrics object"""
        try:
            close = data['Close'].astype(float)
            high = data['High'].astype(float)
            low = data['Low'].astype(float)
            volume = data['Volume'].astype(float)
            
            # Calculate indicators
            ma20 = close.rolling(20).mean()
            ma50 = close.rolling(50).mean()
            ma200 = close.rolling(200).mean()
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd = ema12 - ema26
            signal_line = macd.ewm(span=9).mean()
            
            # ATR
            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(14).mean()
            
            # Volume SMA
            vol_sma = volume.rolling(20).mean()
            
            # Extract last values safely for scalars
            try:
                last_close = float(close.iloc[-1])
                if not self._is_valid_number(last_close) or last_close <= 0:
                    self.logger.warning(f"{ticker}: Invalid latest close price - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing latest close price - skipping")
                return None
                
            try:
                last_ma20 = float(ma20.iloc[-1])
                if not self._is_valid_number(last_ma20):
                    self.logger.warning(f"{ticker}: Invalid MA20 - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing MA20 - skipping")
                return None
                
            try:
                last_ma50 = float(ma50.iloc[-1])
                if not self._is_valid_number(last_ma50):
                    self.logger.warning(f"{ticker}: Invalid MA50 - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing MA50 - skipping")
                return None
                
            try:
                last_ma200 = float(ma200.iloc[-1])
                if not self._is_valid_number(last_ma200):
                    self.logger.warning(f"{ticker}: Invalid MA200 - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing MA200 - skipping")
                return None
                
            try:
                last_rsi = float(rsi.iloc[-1])
                if not self._is_valid_number(last_rsi):
                    self.logger.warning(f"{ticker}: Invalid RSI - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing RSI - skipping")
                return None
                
            try:
                last_macd = float(macd.iloc[-1])
                if not self._is_valid_number(last_macd):
                    self.logger.warning(f"{ticker}: Invalid MACD - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing MACD - skipping")
                return None
                
            try:
                last_signal = float(signal_line.iloc[-1])
                if not self._is_valid_number(last_signal):
                    self.logger.warning(f"{ticker}: Invalid MACD signal - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing MACD signal - skipping")
                return None
                
            try:
                last_atr = float(atr.iloc[-1])
                if not self._is_valid_number(last_atr) or last_atr <= 0:
                    self.logger.warning(f"{ticker}: Invalid ATR - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing ATR - skipping")
                return None
                
            try:
                last_vol = float(volume.iloc[-1])
                if not self._is_valid_number(last_vol):
                    self.logger.warning(f"{ticker}: Invalid volume - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing volume - skipping")
                return None
                
            try:
                last_vol_sma = float(vol_sma.iloc[-1])
                if not self._is_valid_number(last_vol_sma):
                    self.logger.warning(f"{ticker}: Invalid average volume - skipping")
                    return None
            except:
                self.logger.warning(f"{ticker}: Missing average volume - skipping")
                return None
                
            try:
                high_52w = float(close.tail(252).max())
                if not self._is_valid_number(high_52w) or high_52w <= 0:
                    high_52w = last_close
            except:
                high_52w = last_close
                
            try:
                low_52w = float(close.tail(252).min())
                if not self._is_valid_number(low_52w) or low_52w <= 0:
                    low_52w = last_close
            except:
                low_52w = last_close
            
            volume_trend = "stable"
            if last_vol_sma > 0 and last_vol > last_vol_sma * 1.2:
                volume_trend = "increasing"
            elif last_vol_sma > 0 and last_vol < last_vol_sma * 0.8:
                volume_trend = "decreasing"
            
            metrics = TechnicalMetrics(
                current_price=last_close,
                sma_20=last_ma20,
                sma_200=last_ma200,
                rsi_14=last_rsi,
                macd_line=last_macd,
                macd_signal=last_signal,
                macd_histogram=last_macd - last_signal,
                atr_14=last_atr,
                current_volume=int(last_vol),
                avg_volume_20d=int(last_vol_sma),
                volume_trend=volume_trend,
                price_52w_high=high_52w,
                price_52w_low=low_52w,
                price_52w_avg=(high_52w + low_52w) / 2
            )
            return metrics
        except Exception as e:
            self.logger.error(f"Error building metrics for {ticker}: {str(e)}")
            return None
    
    def generate_signal(self, ticker, data):
        try:
            # Build metrics
            metrics = self.build_technical_metrics(ticker, data)
            if metrics is None:
                return None
            
            # Analyze using module
            trend, analysis_details = self.tech_analyzer.analyze(metrics)
            
            # Calculate ATR for targets and stops
            close = data['Close'].astype(float)
            high = data['High'].astype(float)
            low = data['Low'].astype(float)
            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = float(tr.rolling(14).mean().iloc[-1])
            if not self._is_valid_number(atr):
                atr = metrics.atr_14
            if not self._is_valid_number(atr):
                self.logger.warning(f"{ticker}: Invalid ATR - skipping")
                return None
            
            current = metrics.current_price
            if not self._is_valid_number(current) or current <= 0:
                self.logger.warning(f"{ticker}: Invalid current price - skipping")
                return None
            ma50_value = float(close.rolling(50).mean().iloc[-1])
            if not self._is_valid_number(ma50_value):
                self.logger.warning(f"{ticker}: Invalid MA50 - skipping")
                return None
            atr_percent = (atr / current) * 100
            if not self._is_valid_number(atr_percent):
                self.logger.warning(f"{ticker}: Invalid ATR percent - skipping")
                return None
            
            # Generate signal based on trend assessment
            if trend == "uptrend":
                signal = "BUY"
                buy_low = current * 0.98
                buy_high = current * 1.02
                stop = current - (atr * 2)
                target = current + (atr * 5)
                confidence = min(100, 70 + (metrics.rsi_14 - 50) * 0.5)
            elif trend == "downtrend":
                signal = "SELL"
                buy_low, buy_high = None, None
                stop = current + (atr * 2)
                target = current - (atr * 5)
                confidence = min(100, 70 + (50 - metrics.rsi_14) * 0.5)
            else:  # weak_trend
                signal = "HOLD"
                buy_low, buy_high = None, None
                stop = current - (atr * 1.5)
                target = current + (atr * 2)
                confidence = 40
            
            rr = abs((target - current) / (current - stop)) if abs(current - stop) > 0.01 else 0
            
            return {
                'Ticker': ticker,
                'Signal': signal,
                'Current_Price': round(current, 2),
                'Trend_Assessment': trend,
                'MA20': round(metrics.sma_20, 2),
                'MA200': round(metrics.sma_200, 2),
                'RSI': round(metrics.rsi_14, 2),
                'MACD': round(metrics.macd_line, 2),
                'ATR': round(atr, 2),
                'ATR_Percent': round(atr_percent, 2),
                'Buy_Range_Low': round(buy_low, 2) if buy_low else None,
                'Buy_Range_High': round(buy_high, 2) if buy_high else None,
                'Stop_Loss': round(stop, 2),
                'Target': round(target, 2),
                'RR_Ratio': round(rr, 2),
                'Analysis_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Confidence': min(100, int(confidence)),
                'MA50': round(ma50_value, 2),
                'Rules_Passed': len(self.tech_analyzer.rules_passed) if hasattr(self.tech_analyzer, 'rules_passed') else 0,
                'Rules_Failed': len(self.tech_analyzer.rules_failed) if hasattr(self.tech_analyzer, 'rules_failed') else 0
            }
        except Exception as e:
            self.logger.error(f"Error analyzing {ticker}: {str(e)}")
            return None
    
    def analyze_all(self, cache):
        self.logger.info("Starting Enhanced Technical Analysis (Using technical_analysis.py module)...")
        for ticker, data in cache.items():
            result = self.generate_signal(ticker, data)
            if result:
                self.results.append(result)
        self.logger.info(f"[OK] Analyzed {len(self.results)} stocks using module-based approach")
        return self.results

# PHASE 19.3 ENHANCEMENT
class Phase19_3Enhancer:
    def __init__(self, logger):
        self.logger = logger
    
    def enhance(self, results):
        self.logger.info("Applying Phase 19.3 enhancements...")
        for result in results:
            if result['Signal'] == 'BUY' and result['Buy_Range_Low']:
                low, high = result['Buy_Range_Low'], result['Buy_Range_High']
                span = high - low
                opt_upper = low + (span * 0.40)
                result['Entry_Quality'] = {
                    'Optimal_Entry_Zone': {'Range_Low': round(low, 2), 'Range_High': round(opt_upper, 2)},
                    'Extended_Entry_Zone': {'Range_Low': round(opt_upper, 2), 'Range_High': round(high, 2)}
                }
            
            rsi = result.get('RSI', 50)
            if result['Signal'] == 'BUY':
                if rsi >= 70:
                    result['RSI_Warning'] = "OVERBOUGHT (RSI >= 70) - Consider partial entry"
                elif rsi >= 60:
                    result['RSI_Note'] = "Strong (RSI 60-70)"
            elif result['Signal'] == 'SELL':
                if rsi <= 30:
                    result['RSI_Warning'] = "OVERSOLD (RSI <= 30) - Consider covering shorts"
                elif rsi <= 40:
                    result['RSI_Note'] = "Weak (RSI 30-40)"
            
            atr_percent = result.get('ATR_Percent', 0)
            if atr_percent < 2:
                result['Risk_Context'] = "LOW"
            elif atr_percent <= 4:
                result['Risk_Context'] = "NORMAL"
            else:
                result['Risk_Context'] = "ELEVATED"
        
        self.logger.info(f"[OK] Enhanced {len(results)} signals with Phase 19.3 rules")
        return results

# OUTPUT GENERATOR
class OutputGenerator:
    def __init__(self, logger):
        self.logger = logger
        self.ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def _is_valid_number(self, value):
        return not pd.isna(value) and np.isfinite(value)
    
    def _is_valid_result(self, result):
        if result.get('Signal') not in {'BUY', 'HOLD', 'SELL'}:
            return False
        required_numeric = [
            'Current_Price', 'RSI', 'MACD', 'MA20', 'MA50', 'MA200',
            'ATR', 'ATR_Percent', 'Stop_Loss', 'Target', 'RR_Ratio',
            'Confidence', 'Rules_Passed', 'Rules_Failed'
        ]
        for key in required_numeric:
            value = result.get(key)
            if not self._is_valid_number(value):
                return False
            if key in {'Current_Price', 'ATR'} and value <= 0:
                return False
            if key == 'Confidence' and not 0 <= value <= 100:
                return False
        return True
    
    def _validated_results(self, results):
        valid = [result for result in results if self._is_valid_result(result)]
        dropped = len(results) - len(valid)
        if dropped:
            self.logger.warning(f"Dropped {dropped} invalid result rows before output")
        return valid
    
    def generate_all(self, results):
        self.logger.info("Generating outputs...")
        results = self._validated_results(results)
        files = []
        
        # CSV
        try:
            csv_file = Config.OUTPUT_DIR / f'NIFTY50_WEEKLY_ENHANCED_{self.ts}.csv'
            keys = ['Ticker', 'Signal', 'Current_Price', 'Trend_Assessment', 'RSI', 'MACD', 'MA20', 'MA50', 'MA200', 'ATR', 'ATR_Percent',
                    'Buy_Range_Low', 'Buy_Range_High', 'Stop_Loss', 'Target', 'RR_Ratio', 'Risk_Context', 'Confidence', 'Rules_Passed', 'Rules_Failed']
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(results)
            self.logger.info(f"[OK] CSV: {csv_file.name}")
            files.append(str(csv_file))
        except Exception as e:
            self.logger.error(f"CSV generation failed: {str(e)}")
        
        # JSON
        try:
            json_file = Config.OUTPUT_DIR / f'NIFTY50_WEEKLY_ENHANCED_{self.ts}.json'
            output = {
                'Metadata': {
                    'Generated_Date': datetime.now().isoformat(),
                    'Analysis_Type': 'Enhanced Technical (technical_analysis.py module) + Phase 19.3',
                    'Total_Stocks': len(results),
                    'Signal_Summary': {
                        'BUY': sum(1 for r in results if r['Signal'] == 'BUY'),
                        'HOLD': sum(1 for r in results if r['Signal'] == 'HOLD'),
                        'SELL': sum(1 for r in results if r['Signal'] == 'SELL')
                    }
                },
                'Recommendations': results
            }
            with open(json_file, 'w') as f:
                json.dump(output, f, indent=2, allow_nan=False)
            self.logger.info(f"[OK] JSON: {json_file.name}")
            files.append(str(json_file))
        except Exception as e:
            self.logger.error(f"JSON generation failed: {str(e)}")
        
        # Markdown Report
        try:
            md_file = Config.OUTPUT_DIR / f'NIFTY50_WEEKLY_ENHANCED_{self.ts}_REPORT.md'
            with open(md_file, 'w') as f:
                f.write(f"# NIFTY50 Enhanced Technical Analysis (Module-Based)\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Analysis Engine:** technical_analysis.py module + Phase 19.3 enhancements\n\n")
                
                buy_cnt = sum(1 for r in results if r['Signal'] == 'BUY')
                hold_cnt = sum(1 for r in results if r['Signal'] == 'HOLD')
                sell_cnt = sum(1 for r in results if r['Signal'] == 'SELL')
                f.write(f"## Summary\n- **BUY:** {buy_cnt}\n- **HOLD:** {hold_cnt}\n- **SELL:** {sell_cnt}\n\n")
                
                for signal in ['BUY', 'HOLD', 'SELL']:
                    f.write(f"## {signal} ({sum(1 for r in results if r['Signal'] == signal)})\n\n")
                    for r in sorted([x for x in results if x['Signal'] == signal], key=lambda x: x['Confidence'], reverse=True):
                        f.write(f"### {r['Ticker']}\n| Metric | Value |\n|--------|-------|\n")
                        f.write(f"| Price | {r['Current_Price']} |\n| Trend | {r['Trend_Assessment']} |\n")
                        f.write(f"| RSI | {r['RSI']} |\n| MACD | {r['MACD']} |\n")
                        f.write(f"| MA20 | {r['MA20']} |\n| MA200 | {r['MA200']} |\n")
                        f.write(f"| ATR | {r['ATR']} |\n| Risk | {r.get('Risk_Context', 'N/A')} |\n")
                        f.write(f"| Stop Loss | {r['Stop_Loss']} |\n| Target | {r['Target']} |\n| R:R Ratio | {r['RR_Ratio']} |\n")
                        f.write(f"| Confidence | {r['Confidence']}% |\n\n")
                        f.write(f"| Confidence | {r['Confidence']}% | Rules Passed | {r['Rules_Passed']} | Rules Failed | {r['Rules_Failed']} |\n\n")
                        if 'RSI_Warning' in r:
                            f.write(f"⚠️ **Warning:** {r['RSI_Warning']}\n\n")
            self.logger.info(f"[OK] Report: {md_file.name}")
            files.append(str(md_file))
        except Exception as e:
            self.logger.error(f"Markdown report generation failed: {str(e)}")
        
        return files

# ORCHESTRATOR
class Orchestrator:
    def __init__(self):
        self.logger, self.log_file = setup_logging()
        self.start = datetime.now()
    
    def run(self):
        try:
            self.logger.info("=" * 80)
            self.logger.info("NIFTY50 ENHANCED WEEKLY AUTOMATION - STARTING")
            self.logger.info("Using technical_analysis.py module for accurate signal generation")
            self.logger.info("=" * 80)
            
            # Step 1: Collect data
            self.logger.info("\n[STEP 1] COLLECTING MARKET DATA")
            collector = DataCollector(self.logger)
            successful, _ = collector.fetch_all()
            if successful == 0:
                self.logger.error("[ERROR] No data collected. Aborting.")
                return False
            
            # Step 2: Analyze with enhanced module-based engine
            self.logger.info("\n[STEP 2] ENHANCED TECHNICAL ANALYSIS (Module-Based)")
            analyzer = EnhancedAnalysisEngine(self.logger)
            results = analyzer.analyze_all(collector.data_cache)
            if not results:
                self.logger.error("[ERROR] No analysis results. Aborting.")
                return False
            
            # Step 3: Enhance
            self.logger.info("\n[STEP 3] PHASE 19.3 OUTPUT ENHANCEMENT")
            enhancer = Phase19_3Enhancer(self.logger)
            results = enhancer.enhance(results)
            
            # Step 4: Generate outputs
            self.logger.info("\n[STEP 4] GENERATING OUTPUT FILES")
            generator = OutputGenerator(self.logger)
            files = generator.generate_all(results)
            
            # Summary
            self.logger.info("\n" + "=" * 80)
            self.logger.info("ENHANCED WEEKLY AUTOMATION - COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 80)
            
            buy = sum(1 for r in results if r['Signal'] == 'BUY')
            hold = sum(1 for r in results if r['Signal'] == 'HOLD')
            sell = sum(1 for r in results if r['Signal'] == 'SELL')
            
            self.logger.info(f"\nSignal Summary:")
            self.logger.info(f"  [BUY]  {buy:2} stocks")
            self.logger.info(f"  [HOLD] {hold:2} stocks")
            self.logger.info(f"  [SELL] {sell:2} stocks")
            self.logger.info(f"\nOutput Files:")
            for f in files:
                self.logger.info(f"  [OK] {Path(f).name}")
            
            elapsed = (datetime.now() - self.start).total_seconds()
            self.logger.info(f"\nExecution Time: {elapsed:.1f}s | Log: {self.log_file}\n")
            return True
        except Exception as e:
            self.logger.error(f"\n[ERROR] ENHANCED AUTOMATION FAILED: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

if __name__ == '__main__':
    orch = Orchestrator()
    success = orch.run()
    sys.exit(0 if success else 1)
