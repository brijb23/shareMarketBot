"""
Unit tests for Fundamental Analysis
"""

import pytest
from src.data_models import FundamentalMetrics
from src.fundamental_analysis import FundamentalAnalyzer


@pytest.fixture
def analyzer():
    return FundamentalAnalyzer()


@pytest.fixture
def strong_fundamentals():
    """Create strong fundamental metrics"""
    return FundamentalMetrics(
        net_profit_margin=20.0,
        roe=20.0,
        roce=22.0,
        revenue_cagr_5yr=10.0,
        eps_cagr_5yr=12.0,
        profit_cagr_5yr=11.0,
        debt_to_equity=0.5,
        current_ratio=1.5,
        debt_service_coverage=5.0,
        pe_ratio=25.0,
        pb_ratio=2.5,
        dividend_yield=2.0,
        pe_percentile=60.0,
    )


@pytest.fixture
def weak_fundamentals():
    """Create weak fundamental metrics"""
    return FundamentalMetrics(
        net_profit_margin=2.0,
        roe=5.0,
        roce=6.0,
        revenue_cagr_5yr=2.0,
        eps_cagr_5yr=1.0,
        profit_cagr_5yr=0.5,
        debt_to_equity=3.0,
        current_ratio=0.5,
        debt_service_coverage=0.5,
        pe_ratio=50.0,
        pb_ratio=5.0,
        dividend_yield=0.2,
        pe_percentile=90.0,
    )


def test_strong_fundamentals_pass(analyzer, strong_fundamentals):
    """Test that strong fundamentals pass all checks"""
    is_sound, details = analyzer.analyze(strong_fundamentals)
    assert is_sound is True


def test_weak_fundamentals_fail(analyzer, weak_fundamentals):
    """Test that weak fundamentals fail checks"""
    is_sound, details = analyzer.analyze(weak_fundamentals)
    assert is_sound is False


def test_profitability_check(analyzer):
    """Test profitability rule"""
    low_margin = FundamentalMetrics(
        net_profit_margin=2.0,  # Below threshold
        roe=15.0,
        roce=16.0,
        revenue_cagr_5yr=10.0,
        eps_cagr_5yr=10.0,
        profit_cagr_5yr=10.0,
        debt_to_equity=0.5,
        current_ratio=1.5,
        debt_service_coverage=3.0,
        pe_ratio=25.0,
        pb_ratio=2.5,
        dividend_yield=2.0,
        pe_percentile=60.0,
    )
    
    is_sound, details = analyzer.analyze(low_margin)
    assert details["profitability_ok"] is False


def test_growth_check(analyzer):
    """Test growth rule"""
    slow_growth = FundamentalMetrics(
        net_profit_margin=15.0,
        roe=15.0,
        roce=16.0,
        revenue_cagr_5yr=5.0,  # Below 8% threshold
        eps_cagr_5yr=10.0,
        profit_cagr_5yr=10.0,
        debt_to_equity=0.5,
        current_ratio=1.5,
        debt_service_coverage=3.0,
        pe_ratio=25.0,
        pb_ratio=2.5,
        dividend_yield=2.0,
        pe_percentile=60.0,
    )
    
    is_sound, details = analyzer.analyze(slow_growth)
    assert details["growth_ok"] is False


def test_fundamental_score(analyzer, strong_fundamentals, weak_fundamentals):
    """Test fundamental scoring"""
    strong_score = analyzer.get_fundamental_score(strong_fundamentals)
    weak_score = analyzer.get_fundamental_score(weak_fundamentals)
    
    assert strong_score > weak_score
    assert 0 <= strong_score <= 100
    assert 0 <= weak_score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
