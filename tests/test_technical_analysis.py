"""
Unit tests for Technical Analysis
"""

import pytest
from src.data_models import TechnicalMetrics
from src.technical_analysis import TechnicalAnalyzer


@pytest.fixture
def analyzer():
    return TechnicalAnalyzer()


@pytest.fixture
def uptrend_metrics():
    """Create uptrend technical metrics"""
    return TechnicalMetrics(
        current_price=3500.0,
        price_52w_high=3600.0,
        price_52w_low=2800.0,
        price_52w_avg=3200.0,
        sma_20=3400.0,
        sma_200=3300.0,
        rsi_14=65.0,
        macd_line=100.0,
        macd_signal=90.0,
        macd_histogram=10.0,
        atr_14=50.0,
        avg_volume_20d=2500000,
        current_volume=3000000,
        volume_trend="increasing",
    )


@pytest.fixture
def downtrend_metrics():
    """Create downtrend technical metrics"""
    return TechnicalMetrics(
        current_price=2900.0,
        price_52w_high=3600.0,
        price_52w_low=2800.0,
        price_52w_avg=3200.0,
        sma_20=3000.0,
        sma_200=3200.0,
        rsi_14=30.0,
        macd_line=70.0,
        macd_signal=90.0,
        macd_histogram=-20.0,
        atr_14=60.0,
        avg_volume_20d=2500000,
        current_volume=2000000,
        volume_trend="decreasing",
    )


def test_uptrend_detection(analyzer, uptrend_metrics):
    """Test uptrend detection"""
    trend, details = analyzer.analyze(uptrend_metrics)
    assert trend == "uptrend"


def test_downtrend_detection(analyzer, downtrend_metrics):
    """Test downtrend detection"""
    trend, details = analyzer.analyze(downtrend_metrics)
    assert trend == "downtrend"


def test_sma_analysis(analyzer):
    """Test moving average analysis"""
    # Price above both SMAs
    above_both = TechnicalMetrics(
        current_price=3500.0,
        price_52w_high=3600.0,
        price_52w_low=2800.0,
        price_52w_avg=3200.0,
        sma_20=3400.0,
        sma_200=3300.0,
        rsi_14=55.0,
        macd_line=95.0,
        macd_signal=90.0,
        macd_histogram=5.0,
        atr_14=50.0,
        avg_volume_20d=2500000,
        current_volume=2800000,
        volume_trend="stable",
    )
    
    price_trend = analyzer._analyze_moving_averages(above_both)
    assert price_trend == "above_200sma_and_20sma"


def test_momentum_analysis(analyzer):
    """Test momentum indicator analysis"""
    positive_momentum = TechnicalMetrics(
        current_price=3300.0,
        price_52w_high=3600.0,
        price_52w_low=2800.0,
        price_52w_avg=3200.0,
        sma_20=3200.0,
        sma_200=3100.0,
        rsi_14=60.0,
        macd_line=100.0,
        macd_signal=90.0,
        macd_histogram=10.0,
        atr_14=50.0,
        avg_volume_20d=2500000,
        current_volume=2800000,
        volume_trend="stable",
    )
    
    momentum = analyzer._analyze_momentum(positive_momentum)
    assert momentum == "positive"


def test_timing_score(analyzer, uptrend_metrics, downtrend_metrics):
    """Test timing score"""
    uptrend_score = analyzer.get_timing_score(uptrend_metrics)
    downtrend_score = analyzer.get_timing_score(downtrend_metrics)
    
    # Uptrend should score higher
    assert uptrend_score > downtrend_score
    assert 0 <= uptrend_score <= 100
    assert 0 <= downtrend_score <= 100


def test_entry_timing_recommendation(analyzer, uptrend_metrics, downtrend_metrics):
    """Test entry timing recommendations"""
    uptrend_entry = analyzer.get_entry_timing(uptrend_metrics)
    downtrend_entry = analyzer.get_entry_timing(downtrend_metrics)
    
    assert "Accumulate" in uptrend_entry or "entry" in uptrend_entry.lower()
    assert "Avoid" in downtrend_entry or "avoid" in downtrend_entry.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
