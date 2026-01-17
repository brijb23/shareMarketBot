"""
Backtest Package - Historical Analysis & Testing

Modules:
- snapshot: Capture analysis state at a point in time
- simulator: Run analysis on historical data
- evaluator: Compare past recommendations vs actual outcomes
- metrics: Generate reports and statistics
"""

from . import snapshot
from . import simulator
from . import evaluator
from . import metrics

__all__ = [
    "snapshot",
    "simulator",
    "evaluator",
    "metrics",
]
