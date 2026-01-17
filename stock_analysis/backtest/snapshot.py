"""
Snapshot Generator

Captures complete analysis state at a single point in time.
Snapshots are immutable - frozen historical records for backtesting.
Now integrated with improvement modules for less conservative decisions.
"""

import json
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from stock_analysis.common.models import Snapshot
from stock_analysis.data.base_provider import PriceDataProvider, FundamentalDataProvider
from stock_analysis.analysis.indicators import IndicatorEngine
from stock_analysis.analysis.fundamentals import FundamentalAnalyzer
from stock_analysis.analysis.technicals import TechnicalAnalyzer
from stock_analysis.common.momentum_score import MomentumScorer
from stock_analysis.common.stock_classifier import StockClassifier

# Import improvement modules
try:
    # Add src directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
    from convergence_detector import ConvergenceDetector
    from volatility_adjusted_scoring import VolatilityAdjustedScoring
    from decision_engine import DecisionEngine
    from constants import STOCK_TYPE_THRESHOLDS
except ImportError:
    # Fallback if imports fail
    ConvergenceDetector = None
    VolatilityAdjustedScoring = None
    DecisionEngine = None
    STOCK_TYPE_THRESHOLDS = None


def _generate_improved_decision(fund_total, tech_total, momentum_score, 
                               stock_type, convergence_detected, fundamental_trend):
    """
    Generate improved, less-conservative decision based on stock type.
    This function applies stock-type-specific thresholds and rules.
    """
    
    # Define thresholds by stock type
    thresholds = {
        'blue_chip': {'fund': 65, 'tech': 65, 'momentum': 60},
        'psu_government': {'fund': 55, 'tech': 60, 'momentum': 60},
        'recovery_turnaround': {'fund': 50, 'tech': 65, 'momentum': 65},
        'cyclical_volatile': {'fund': 60, 'tech': 70, 'momentum': 65}
    }
    
    # Get thresholds for this stock type (default to blue_chip if unknown)
    t = thresholds.get(stock_type, thresholds['blue_chip'])
    
    # Decision logic based on stock type and scores
    stock_type_label = f" [{stock_type}]"
    
    # CONVERGENCE SIGNAL (highest priority - institutional accumulation)
    if convergence_detected:
        return f"ACCUMULATE - CONVERGENCE SIGNAL{stock_type_label}. Tech: {tech_total:.0f}/100, Momentum: {momentum_score:.0f}/100, Fund Trend: {fundamental_trend}"
    
    # ACCUMULATE decisions (using strict type-specific thresholds)
    # For cyclical stocks: MUST have tech >= threshold
    if stock_type == 'cyclical_volatile':
        if fund_total >= t['fund'] and tech_total >= t['tech']:
            return f"ACCUMULATE - Strong on both metrics{stock_type_label}. Fund: {fund_total:.0f}/100, Tech: {tech_total:.0f}/100"
        # For cyclical, if tech < threshold, never ACCUMULATE
        if tech_total < t['tech']:
            # Fall through to HOLD logic
            pass
        else:
            # Tech meets threshold
            if fund_total >= t['fund'] - 5:
                return f"ACCUMULATE - Cyclical confirmed on technicals{stock_type_label}. Fund: {fund_total:.0f}/100, Tech: {tech_total:.0f}/100"
    else:
        # For non-cyclical stocks
        if fund_total >= t['fund'] and tech_total >= t['tech']:
            return f"ACCUMULATE - Strong on both metrics{stock_type_label}. Fund: {fund_total:.0f}/100, Tech: {tech_total:.0f}/100"
        
        if fund_total >= t['fund'] and tech_total >= t['tech'] - 10:
            return f"ACCUMULATE - Excellent fundamentals, solid technicals{stock_type_label}. Fund: {fund_total:.0f}/100, Tech: {tech_total:.0f}/100"
    
    # Special handling for recovery stocks - lower fund threshold if tech is strong
    if stock_type == 'recovery_turnaround' and fundamental_trend == 'improving':
        if tech_total >= 70 and momentum_score >= 65 and fund_total >= 45:
            return f"ACCUMULATE - RECOVERY PLAY{stock_type_label}. Strong technicals with improving fundamentals. Tech: {tech_total:.0f}/100, Momentum: {momentum_score:.0f}/100"
    
    # Special handling for PSU/Government stocks - lower threshold entry
    if stock_type == 'psu_government' and fundamental_trend in ['improving', 'stable']:
        if fund_total >= 55 and tech_total >= 55 and momentum_score >= 55:
            return f"ACCUMULATE - PSU OPPORTUNITY{stock_type_label}. Fund: {fund_total:.0f}/100, Tech: {tech_total:.0f}/100, Policy tailwind detected"
    
    # HOLD decisions (meets minimum but not accumulate)
    if fund_total >= t['fund'] - 10 and tech_total >= t['tech'] - 15:
        return f"HOLD - Good fundamentals, waiting for technical confirmation{stock_type_label}. Fund: {fund_total:.0f}/100, Tech: {tech_total:.0f}/100"
    
    if tech_total >= t['tech'] - 5 and fund_total >= t['fund'] - 20 and momentum_score >= 60:
        return f"HOLD - Strong technicals with building momentum{stock_type_label}. Tech: {tech_total:.0f}/100, Momentum: {momentum_score:.0f}/100"
    
    if tech_total >= t['tech'] - 10 and momentum_score >= t['momentum']:
        return f"HOLD - Good technicals with momentum, monitor fundamentals{stock_type_label}. Tech: {tech_total:.0f}/100, Momentum: {momentum_score:.0f}/100"
    
    # AVOID decisions (poor on multiple metrics)
    if fund_total < t['fund'] - 15 and tech_total < t['tech'] - 10:
        return f"AVOID - Weak on multiple metrics{stock_type_label}. Fund: {fund_total:.0f}/100, Tech: {tech_total:.0f}/100"
    
    # DEFAULT: HOLD (unclear/mixed signals)
    return f"HOLD - Mixed signals, awaiting clarity{stock_type_label}. Fund: {fund_total:.0f}/100, Tech: {tech_total:.0f}/100, Momentum: {momentum_score:.0f}/100"


class SnapshotGenerator:
    """
    Generate immutable snapshots of analysis at specific points in time.
    
    Purpose:
    - Record what analysis showed on a given date
    - Enable backtesting of past decisions
    - Compare forecasts vs actual outcomes
    - Preserve historical state for audit trails
    
    Key Principles:
    - No future data leakage (only data available as_of_date)
    - Immutable once created (no recalculation)
    - Complete capture of analysis state
    
    Example:
        generator = SnapshotGenerator(price_provider, fund_provider)
        snapshot = generator.generate_snapshot(
            symbol="TCS",
            as_of_date=datetime(2024, 1, 15),
            nifty_provider=nifty_provider
        )
    """
    
    def __init__(self, price_provider: PriceDataProvider,
                 fundamental_provider: FundamentalDataProvider):
        """
        Initialize snapshot generator.
        
        Args:
            price_provider: PriceDataProvider implementation (Yahoo, CSV, etc.)
            fundamental_provider: FundamentalDataProvider implementation
        
        Raises:
            ValueError: If providers invalid
        """
        if not isinstance(price_provider, PriceDataProvider):
            raise ValueError(f"price_provider must implement PriceDataProvider")
        
        if not isinstance(fundamental_provider, FundamentalDataProvider):
            raise ValueError(f"fundamental_provider must implement FundamentalDataProvider")
        
        self.price_provider = price_provider
        self.fund_provider = fundamental_provider
    
    def generate_snapshot(self, symbol: str, as_of_date: datetime,
                         nifty_provider: PriceDataProvider = None) -> Snapshot:
        """
        Generate complete analysis snapshot at specific date.
        
        Steps:
        1. Fetch price data up to as_of_date (no future data)
        2. Calculate technical indicators
        3. Fetch fundamental data valid as_of_date
        4. Score fundamentals and technicals
        5. Freeze into immutable Snapshot
        
        Args:
            symbol: Stock symbol (e.g., "TCS", "TCS.NS")
            as_of_date: Reference date (datetime). Only use data <= this date.
            nifty_provider: Optional provider for NIFTY index (for relative strength)
        
        Returns:
            Snapshot object with all analysis frozen in time
        
        Raises:
            ValueError: If symbol invalid or as_of_date invalid
            ConnectionError: If data providers unavailable
            FileNotFoundError: If data files missing
        
        Example:
            >>> generator = SnapshotGenerator(price_prov, fund_prov)
            >>> snapshot = generator.generate_snapshot(
            ...     "INFY.NS",
            ...     datetime(2024, 1, 15),
            ...     nifty_provider
            ... )
            >>> print(f"Snapshot date: {snapshot.snapshot_date}")
            >>> print(f"Price: {snapshot.price_bar.close}")
        """
        try:
            # Validate inputs
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError(f"symbol must be non-empty string, got {repr(symbol)}")
            
            if not isinstance(as_of_date, datetime):
                raise ValueError(f"as_of_date must be datetime, got {type(as_of_date).__name__}")
            
            symbol = symbol.strip()
            
            # Step 1: Fetch price history (up to as_of_date)
            # Use lookback of ~250 days to have sufficient data for indicators
            from datetime import timedelta
            lookback_days = 300
            start_date = as_of_date - timedelta(days=lookback_days)
            
            price_df = self.price_provider.get_price_history(
                symbol, start_date, as_of_date
            )
            
            if price_df.empty:
                raise ValueError(f"No price data for {symbol} up to {as_of_date.date()}")
            
            # Get latest price bar as_of_date
            latest_price_row = price_df.iloc[-1]
            latest_price = float(latest_price_row['close'])
            
            # Step 2: Calculate technical indicators
            # Get NIFTY data if provider available
            if nifty_provider is not None:
                try:
                    nifty_df = nifty_provider.get_price_history(
                        "^NSEI", start_date, as_of_date
                    )
                except:
                    nifty_df = None
            else:
                nifty_df = None
            
            # Calculate indicators
            indicator_engine = IndicatorEngine()
            indicators = indicator_engine.calculate_indicators(
                price_df=price_df,
                index_df=nifty_df if nifty_df is not None else price_df,
                as_of_date=as_of_date,
                symbol=symbol
            )
            
            if indicators is None:
                raise ValueError(f"Could not calculate indicators for {symbol}")
            
            # Step 3: Fetch fundamental data valid as_of_date
            fundamentals = self.fund_provider.get_fundamentals(symbol, as_of_date)
            
            if fundamentals is None:
                raise ValueError(f"No fundamental data for {symbol} as of {as_of_date.date()}")
            
            # Step 4: Score fundamentals and technicals
            fund_analyzer = FundamentalAnalyzer()
            fundamental_score = fund_analyzer.score_fundamentals(fundamentals)
            
            tech_analyzer = TechnicalAnalyzer()
            technical_score = tech_analyzer.score_technical(indicators)
            
            # NEW: Calculate momentum score using price data
            try:
                momentum_score = MomentumScorer.calculate_momentum_score(price_df, as_of_date)
            except:
                momentum_score = 50
            
            # NEW: Calculate fundamental trend
            try:
                if hasattr(self.fund_provider, 'calculate_fundamental_trend'):
                    fundamental_trend = self.fund_provider.calculate_fundamental_trend(symbol, as_of_date)
                else:
                    fundamental_trend = {'trend': 'unknown'}
            except:
                fundamental_trend = {'trend': 'unknown'}
            
            # Step 5: Generate decision based on scores using IMPROVED logic
            decision = None
            stock_type = None
            
            try:
                # Get scores
                fund_total = fundamental_score.total_score if fundamental_score and fundamental_score.total_score else 0
                tech_total = technical_score.total_score if technical_score and technical_score.total_score else 0
                
                # Classify stock using IMPROVED classifier (with new types)
                stock_type = StockClassifier.classify_stock(
                    symbol,
                    fundamental_trend=fundamental_trend.get('trend'),
                    fund_score=fund_total
                )
                
                # Adjust technical score for cyclical stocks using volatility adjustment
                if VolatilityAdjustedScoring is not None and stock_type == 'cyclical_volatile':
                    try:
                        tech_total = VolatilityAdjustedScoring.adjust_tech_score(
                            tech_score=tech_total,
                            volatility=indicators.get('volatility', 50) if indicators else 50,
                            trend=fundamental_trend.get('trend', 'unknown')
                        )
                    except:
                        pass  # Use original tech_total if adjustment fails
                
                # Check for convergence signal (institutional accumulation)
                convergence_detected = False
                if ConvergenceDetector is not None and stock_type in ['recovery_turnaround', 'psu_government']:
                    try:
                        convergence_detected = ConvergenceDetector.detect_convergence(
                            tech_score=tech_total,
                            momentum_score=momentum_score,
                            fund_score=fund_total,
                            fundamental_trend=fundamental_trend.get('trend'),
                            stock_type=stock_type
                        )
                    except:
                        convergence_detected = False
                
                # Use improved decision engine if available
                if DecisionEngine is not None:
                    try:
                        engine = DecisionEngine()
                        decision = engine._make_decision_dynamic(
                            fund_score=fund_total,
                            tech_score=tech_total,
                            momentum_score=momentum_score,
                            stock_type=stock_type,
                            convergence_detected=convergence_detected,
                            fundamental_trend=fundamental_trend.get('trend')
                        )
                    except:
                        # Fall back to improved threshold-based logic
                        decision = _generate_improved_decision(
                            fund_total, tech_total, momentum_score, 
                            stock_type, convergence_detected, 
                            fundamental_trend.get('trend')
                        )
                else:
                    # Fall back to improved threshold-based logic
                    decision = _generate_improved_decision(
                        fund_total, tech_total, momentum_score, 
                        stock_type, convergence_detected, 
                        fundamental_trend.get('trend')
                    )
                
            except Exception as e:
                # If all else fails, provide neutral decision
                decision = "AWAITING ANALYSIS - Data incomplete"
                if stock_type is None:
                    stock_type = 'unknown'
            
            # Step 6: Create immutable Snapshot
            snapshot = Snapshot(
                snapshot_date=as_of_date,
                ticker=symbol,
                price_at_date=Decimal(str(latest_price)),
                fundamental_data=fundamentals,
                indicators=indicators,
                fundamental_score=fundamental_score,
                technical_score=technical_score,
                decision=decision,
                momentum_score=momentum_score,
                fundamental_trend=fundamental_trend,
                stock_type=stock_type
            )
            
            return snapshot
            
        except ValueError as e:
            raise
        except ConnectionError as e:
            raise ConnectionError(f"Error fetching data for {symbol}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error generating snapshot for {symbol}: {str(e)}")
    
    @staticmethod
    def save_snapshot(snapshot: Snapshot, filepath: str) -> None:
        """
        Save snapshot to JSON file for later analysis.
        
        Args:
            snapshot: Snapshot object to persist
            filepath: Path to save JSON
        
        Returns:
            None
        
        Raises:
            IOError: If cannot write file
            ValueError: If snapshot invalid
        
        Example:
            >>> SnapshotGenerator.save_snapshot(snapshot, "snapshots/TCS_20240115.json")
        """
        try:
            if not isinstance(snapshot, Snapshot):
                raise ValueError(f"snapshot must be Snapshot, got {type(snapshot).__name__}")
            
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert Snapshot to dict (would need custom serialization)
            # This is a simplified version - in production would use proper serialization
            snapshot_dict = {
                "symbol": snapshot.symbol,
                "snapshot_date": snapshot.snapshot_date.isoformat(),
                "price": snapshot.price,
                "created_at": snapshot.created_at.isoformat(),
                # In production, would serialize all nested objects
            }
            
            with open(filepath, 'w') as f:
                json.dump(snapshot_dict, f, indent=2)
            
        except IOError as e:
            raise IOError(f"Error saving snapshot: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error serializing snapshot: {str(e)}")
    
    @staticmethod
    def load_snapshot(filepath: str) -> Snapshot:
        """
        Load snapshot from JSON file.
        
        Args:
            filepath: Path to snapshot JSON
        
        Returns:
            Reconstructed Snapshot object
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON invalid or incomplete
        
        Example:
            >>> snapshot = SnapshotGenerator.load_snapshot("snapshots/TCS_20240115.json")
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                raise FileNotFoundError(f"Snapshot file not found: {filepath}")
            
            with open(filepath, 'r') as f:
                snapshot_dict = json.load(f)
            
            # Reconstruct Snapshot object (simplified)
            # In production, would fully deserialize all nested objects
            snapshot = Snapshot(
                symbol=snapshot_dict["symbol"],
                snapshot_date=datetime.fromisoformat(snapshot_dict["snapshot_date"]),
                price=snapshot_dict["price"],
                created_at=datetime.fromisoformat(snapshot_dict["created_at"])
            )
            
            return snapshot
            
        except FileNotFoundError as e:
            raise
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in snapshot file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading snapshot: {str(e)}")
