"""
Unit tests for Decision Engine
"""

import pytest
from src.data_models import (
    FundamentalMetrics, TechnicalMetrics, RiskAssessment, Decision
)
from src.decision_engine import DecisionEngine


@pytest.fixture
def decision_engine():
    return DecisionEngine()


@pytest.fixture
def strong_fundamentals():
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


@pytest.fixture
def uptrend_technicals():
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
def downtrend_technicals():
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


@pytest.fixture
def risk_assessment():
    return RiskAssessment(
        atr_pct_of_price=1.5,
        volatility_level="medium",
        max_position_size_pct=5.0,
        suggested_position_size_pct=3.0,
        entry_price=3500.0,
        target_price=4500.0,
        stop_loss_price=3150.0,
        support_level=3300.0,
        risk_reward_ratio=2.5,
        max_drawdown_pct=15.0,
    )


def test_strong_fundamentals_uptrend_accumulate(
    decision_engine, strong_fundamentals, uptrend_technicals, risk_assessment
):
    """Test: Strong fundamentals + Uptrend = ACCUMULATE"""
    analysis = decision_engine.decide(
        ticker="TCS",
        name="Tata Consultancy Services",
        sector="IT",
        fundamentals=strong_fundamentals,
        technicals=uptrend_technicals,
        risk=risk_assessment,
    )
    
    assert analysis.decision == Decision.ACCUMULATE


def test_strong_fundamentals_downtrend_exit(
    decision_engine, strong_fundamentals, downtrend_technicals, risk_assessment
):
    """Test: Strong fundamentals + Downtrend = EXIT"""
    analysis = decision_engine.decide(
        ticker="INFY",
        name="Infosys Limited",
        sector="IT",
        fundamentals=strong_fundamentals,
        technicals=downtrend_technicals,
        risk=risk_assessment,
    )
    
    assert analysis.decision == Decision.EXIT


def test_weak_fundamentals_always_exit(
    decision_engine, weak_fundamentals, uptrend_technicals, risk_assessment
):
    """Test: Weak fundamentals = EXIT regardless of technicals"""
    analysis = decision_engine.decide(
        ticker="BADCO",
        name="Bad Company Ltd",
        sector="FMCG",
        fundamentals=weak_fundamentals,
        technicals=uptrend_technicals,
        risk=risk_assessment,
    )
    
    assert analysis.decision == Decision.EXIT


def test_decision_confidence_score(
    decision_engine, strong_fundamentals, uptrend_technicals, risk_assessment
):
    """Test that confidence scores are reasonable"""
    analysis = decision_engine.decide(
        ticker="TCS",
        name="Tata Consultancy Services",
        sector="IT",
        fundamentals=strong_fundamentals,
        technicals=uptrend_technicals,
        risk=risk_assessment,
    )
    
    assert 0 <= analysis.confidence_score <= 100


def test_decision_has_reasoning(
    decision_engine, strong_fundamentals, uptrend_technicals, risk_assessment
):
    """Test that decisions include reasoning"""
    analysis = decision_engine.decide(
        ticker="TCS",
        name="Tata Consultancy Services",
        sector="IT",
        fundamentals=strong_fundamentals,
        technicals=uptrend_technicals,
        risk=risk_assessment,
    )
    
    assert len(analysis.reasoning) > 0
    assert len(analysis.key_risks) > 0
    assert len(analysis.key_catalysts) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
