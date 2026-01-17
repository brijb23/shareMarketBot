#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIFTY50 WEEKLY AUTOMATION - PRODUCTION READY
Automated trading analysis with Phase 19.2 + 19.3 enhancements
"""

import os, json, csv, pandas as pd, numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from pathlib import Path
import traceback
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# CONFIG
class Config:
    NIFTY50_STOCKS = [
        'NIFTY 500.NS',
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
    TREND_THRESHOLD = 0.5
    MOMENTUM_THRESHOLD = 1.0
    VOLATILITY_LOW = 12
    VOLATILITY_NORMAL = 20
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
    log_file = Config.LOG_DIR / f'WEEKLY_LOG_{timestamp}.txt'
    logger = logging.getLogger('NIFTY50')
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
    def __init__(self, logger):
        self.logger = logger
        self.data_cache = {}
    
    def fetch_stock_data(self, ticker):
        try:
            self.logger.info(f"Fetching {ticker}...")
            data = yf.download(ticker, period='1y', progress=False, timeout=30)
            if data.empty:
                self.logger.warning(f"No data for {ticker}")
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

# ANALYSIS ENGINE
class AnalysisEngine:
    def __init__(self, logger):
        self.logger = logger
        self.results = []
    
    def calc_trend(self, data):
        try:
            close = data['Close'].astype(float)
            ma50 = close.rolling(50).mean()
            current = float(close.iloc[-1])
            ma50_val = float(ma50.iloc[-1])
            if pd.isna(ma50_val) or ma50_val == 0:
                return 0.0
            return ((current - ma50_val) / ma50_val) * 100
        except:
            return 0.0
    
    def calc_momentum(self, data):
        try:
            close = data['Close'].astype(float)
            current = float(close.iloc[-1])
            past = float(close.iloc[-11])
            if past == 0:
                return 0.0
            return ((current - past) / past) * 100
        except:
            return 0.0
    
    def calc_volatility(self, data):
        try:
            close = data['Close'].astype(float)
            returns = close.pct_change()
            vol = float(returns.rolling(20).std().iloc[-1])
            return vol * 100 if not pd.isna(vol) else 0.0
        except:
            return 0.0
    
    def calc_atr(self, data):
        try:
            high, low, close = data['High'], data['Low'], data['Close']
            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            return float(tr.rolling(14).mean().iloc[-1])
        except:
            return 10.0
    
    def generate_signal(self, ticker, data):
        try:
            trend = float(self.calc_trend(data))
            momentum = float(self.calc_momentum(data))
            volatility = float(self.calc_volatility(data))
            current = float(data['Close'].iloc[-1])
            atr = float(self.calc_atr(data))
            
            # Signal logic
            if trend > Config.TREND_THRESHOLD and momentum > Config.MOMENTUM_THRESHOLD:
                signal = "BUY"
                buy_low = current * 0.98
                buy_high = current * 1.02
                stop = current - (atr * 2)
                target = current + (atr * 5)
            elif trend < -Config.TREND_THRESHOLD and momentum < -Config.MOMENTUM_THRESHOLD:
                signal = "SELL"
                buy_low, buy_high = None, None
                stop = current + (atr * 2)
                target = current - (atr * 5)
            else:
                signal = "HOLD"
                buy_low, buy_high = None, None
                stop = current - (atr * 1.5)
                target = current + (atr * 2)
            
            rr = abs((target - current) / (current - stop)) if abs(current - stop) > 0.01 else 0
            
            return {
                'Ticker': ticker,
                'Signal': signal,
                'Current_Price': round(current, 2),
                'Trend_Percent': round(trend, 2),
                'Momentum_Percent': round(momentum, 2),
                'Volatility_Percent': round(volatility, 2),
                'Buy_Range_Low': round(buy_low, 2) if buy_low else None,
                'Buy_Range_High': round(buy_high, 2) if buy_high else None,
                'Stop_Loss': round(stop, 2),
                'Target': round(target, 2),
                'RR_Ratio': round(rr, 2),
                'Analysis_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Confidence': self._confidence(trend, momentum, volatility)
            }
        except Exception as e:
            self.logger.error(f"Error {ticker}: {str(e)[:40]}")
            return None
    
    def _confidence(self, trend, momentum, vol):
        conf = 40
        if abs(trend) > 1:
            conf += 20
        if abs(momentum) > 2:
            conf += 20
        if vol < 15:
            conf += 20
        return min(conf, 100)
    
    def analyze_all(self, cache):
        self.logger.info("Starting Phase 19.2 analysis...")
        for ticker, data in cache.items():
            result = self.generate_signal(ticker, data)
            if result:
                self.results.append(result)
        self.logger.info(f"[OK] Analyzed {len(self.results)} stocks")
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
            
            if result['Volatility_Percent'] <= Config.VOLATILITY_LOW:
                result['Risk_Context'] = "LOW"
            elif result['Volatility_Percent'] <= Config.VOLATILITY_NORMAL:
                result['Risk_Context'] = "NORMAL"
            else:
                result['Risk_Context'] = "ELEVATED"
            
            if result['Signal'] == 'HOLD':
                trend, momentum, vol = result['Trend_Percent'], result['Momentum_Percent'], result['Volatility_Percent']
                rationale = f"HOLD recommended: "
                if abs(trend) < 0.5:
                    rationale += f"Indecisive trend ({trend:.2f}% vs 50-day MA); "
                else:
                    rationale += f"Weak trend ({trend:.2f}% vs 50-day MA); "
                if abs(momentum) < 1:
                    rationale += f"Mixed momentum ({momentum:.2f}% in 10 days) - no conviction; "
                else:
                    rationale += f"Conflicting momentum ({momentum:.2f}% in 10 days); "
                rationale += f"moderate volatility adds uncertainty. Re-evaluate when trend clarifies (>0.5%) or momentum strengthens (>1%). Avoid forced entry/exit."
                result['Hold_Rationale'] = rationale
        
        self.logger.info(f"[OK] Enhanced {len(results)} signals")
        return results

# OUTPUT GENERATOR
class OutputGenerator:
    def __init__(self, logger):
        self.logger = logger
        self.ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def generate_all(self, results):
        self.logger.info("Generating outputs...")
        files = []
        
        # CSV
        try:
            csv_file = Config.OUTPUT_DIR / f'NIFTY50_WEEKLY_{self.ts}.csv'
            keys = ['Ticker', 'Signal', 'Current_Price', 'Trend_Percent', 'Momentum_Percent', 'Volatility_Percent',
                    'Buy_Range_Low', 'Buy_Range_High', 'Stop_Loss', 'Target', 'RR_Ratio', 'Risk_Context', 'Confidence']
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(results)
            self.logger.info(f"[OK] CSV: {csv_file.name}")
            files.append(str(csv_file))
        except:
            pass
        
        # JSON
        try:
            json_file = Config.OUTPUT_DIR / f'NIFTY50_WEEKLY_{self.ts}.json'
            output = {
                'Metadata': {
                    'Generated_Date': datetime.now().isoformat(),
                    'Analysis_Type': 'Phase 19.2 + 19.3',
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
                json.dump(output, f, indent=2)
            self.logger.info(f"[OK] JSON: {json_file.name}")
            files.append(str(json_file))
        except:
            pass
        
        # Markdown Report
        try:
            md_file = Config.OUTPUT_DIR / f'NIFTY50_WEEKLY_{self.ts}_REPORT.md'
            with open(md_file, 'w') as f:
                f.write(f"# NIFTY50 Weekly Analysis\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                buy_cnt = sum(1 for r in results if r['Signal'] == 'BUY')
                hold_cnt = sum(1 for r in results if r['Signal'] == 'HOLD')
                sell_cnt = sum(1 for r in results if r['Signal'] == 'SELL')
                f.write(f"## Summary\n- **BUY:** {buy_cnt}\n- **HOLD:** {hold_cnt}\n- **SELL:** {sell_cnt}\n\n")
                
                for signal in ['BUY', 'HOLD', 'SELL']:
                    f.write(f"## {signal} ({sum(1 for r in results if r['Signal'] == signal)})\n\n")
                    for r in [x for x in results if x['Signal'] == signal]:
                        f.write(f"### {r['Ticker']}\n| Metric | Value |\n|--------|-------|\n")
                        f.write(f"| Price | {r['Current_Price']} |\n| Trend | {r['Trend_Percent']}% |\n")
                        f.write(f"| Momentum | {r['Momentum_Percent']}% |\n| Volatility | {r['Volatility_Percent']}% |\n")
                        f.write(f"| Risk | {r.get('Risk_Context', 'N/A')} |\n| Stop Loss | {r['Stop_Loss']} |\n")
                        f.write(f"| Target | {r['Target']} |\n| R:R | {r['RR_Ratio']} |\n| Conf | {r['Confidence']}% |\n\n")
                        if 'Hold_Rationale' in r:
                            f.write(f"**Rationale:** {r['Hold_Rationale']}\n\n")
            self.logger.info(f"[OK] Report: {md_file.name}")
            files.append(str(md_file))
        except:
            pass
        
        # Text Summary
        try:
            txt_file = Config.OUTPUT_DIR / f'NIFTY50_WEEKLY_{self.ts}_SUMMARY.txt'
            with open(txt_file, 'w') as f:
                f.write(f"NIFTY50 WEEKLY TRADING ANALYSIS\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                buy_list = [r for r in results if r['Signal'] == 'BUY']
                hold_list = [r for r in results if r['Signal'] == 'HOLD']
                sell_list = [r for r in results if r['Signal'] == 'SELL']
                
                f.write(f"BUY SIGNALS ({len(buy_list)}):\n")
                for r in buy_list:
                    f.write(f"  {r['Ticker']:15} | Price: {r['Current_Price']:7.2f} | Entry: {r.get('Buy_Range_Low', 'N/A'):7} | Target: {r['Target']:7.2f} | Risk: {r.get('Risk_Context', 'N/A'):10}\n")
                f.write(f"\nHOLD SIGNALS ({len(hold_list)}):\n")
                for r in hold_list:
                    f.write(f"  {r['Ticker']:15} | Price: {r['Current_Price']:7.2f} | Trend: {r['Trend_Percent']:6.2f}% | Mom: {r['Momentum_Percent']:6.2f}% | Risk: {r.get('Risk_Context', 'N/A'):10}\n")
                f.write(f"\nSELL SIGNALS ({len(sell_list)}):\n")
                for r in sell_list:
                    f.write(f"  {r['Ticker']:15} | Price: {r['Current_Price']:7.2f} | Target: {r['Target']:7.2f} | Risk: {r.get('Risk_Context', 'N/A'):10} | Conf: {r['Confidence']}%\n")
            self.logger.info(f"[OK] Summary: {txt_file.name}")
            files.append(str(txt_file))
        except:
            pass
        
        return files

# ORCHESTRATOR
class Orchestrator:
    def __init__(self):
        self.logger, self.log_file = setup_logging()
        self.start = datetime.now()
    
    def run(self):
        try:
            self.logger.info("=" * 80)
            self.logger.info("NIFTY50 WEEKLY AUTOMATION - STARTING")
            self.logger.info("=" * 80)
            
            # Step 1: Collect data
            self.logger.info("\n[STEP 1] COLLECTING MARKET DATA")
            collector = DataCollector(self.logger)
            successful, _ = collector.fetch_all()
            if successful == 0:
                self.logger.error("[ERROR] No data collected. Aborting.")
                return False
            
            # Step 2: Analyze
            self.logger.info("\n[STEP 2] PHASE 19.2 TRADING ANALYSIS")
            analyzer = AnalysisEngine(self.logger)
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
            self.logger.info("WEEKLY AUTOMATION - COMPLETED SUCCESSFULLY")
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
            self.logger.error(f"\n[ERROR] AUTOMATION FAILED: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

if __name__ == '__main__':
    import sys
    orch = Orchestrator()
    success = orch.run()
    sys.exit(0 if success else 1)
