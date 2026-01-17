"""
Configuration and setup for the analysis engine
"""

import logging
from pathlib import Path

# Logging setup
LOG_LEVEL = logging.INFO
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
SRC_DIR.mkdir(exist_ok=True)
TESTS_DIR.mkdir(exist_ok=True)

# Analysis parameters
ANALYSIS_PARAMS = {
    "min_data_points": 250,  # Minimum trading days
    "lookback_days": 365,  # 1 year for technical analysis
    "quarterly_lookback_years": 5,  # 5 years for fundamentals
}

# Conservative mode: stricter thresholds
CONSERVATIVE_MODE = True

if CONSERVATIVE_MODE:
    # Override with stricter thresholds if needed
    pass
