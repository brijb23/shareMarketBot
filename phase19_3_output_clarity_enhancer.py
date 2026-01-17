"""
PHASE 19.3: OUTPUT-ONLY OPERATOR CLARITY ENHANCEMENT
=====================================================

Pure output-layer enhancements:
1. BUY entry quality zones (Optimal vs Extended)
2. Risk context tags (LOW/NORMAL/ELEVATED) for all signals
3. Explicit HOLD justification for clarity

NON-NEGOTIABLE CONSTRAINTS:
- Zero changes to BUY/HOLD/SELL logic
- Zero changes to entry/stop/target calculations
- Zero changes to R:R ratios
- Zero changes to signal counts
- Purely descriptive, informational metadata only
"""

import json
from pathlib import Path
from datetime import datetime


class BUYEntryQualityAnalyzer:
    """Add entry zone clarity to BUY signals without modifying logic."""
    
    @staticmethod
    def calculate_entry_zones(buy_range_low, buy_range_high):
        """
        Calculate optimal and extended entry zones from existing buy range.
        
        - Optimal Zone: Lower 40% of range (safest entry)
        - Extended Zone: Upper 60% of range (acceptable, higher risk)
        
        Formula: PURELY DESCRIPTIVE - no math changes to stops/targets
        """
        range_span = buy_range_high - buy_range_low
        
        # Optimal: Lower 40% of range
        optimal_upper = buy_range_low + (range_span * 0.40)
        
        # Extended: Entire upper 60% of range
        extended_lower = buy_range_low + (range_span * 0.40)
        extended_upper = buy_range_high
        
        return {
            "Optimal_Entry_Zone": {
                "Range_Low": round(buy_range_low, 2),
                "Range_High": round(optimal_upper, 2),
                "Description": "Safest entry zone - lower 40% of buy range"
            },
            "Extended_Entry_Zone": {
                "Range_Low": round(extended_lower, 2),
                "Range_High": round(extended_upper, 2),
                "Description": "Acceptable entry - upper 60% of buy range, higher risk"
            }
        }


class RiskContextClassifier:
    """Classify risk context based on existing volatility (informational only)."""
    
    @staticmethod
    def classify_risk_context(volatility_percent):
        """
        Map existing volatility to risk context.
        
        LOW:       <= 12% annual volatility
        NORMAL:    13-20% annual volatility
        ELEVATED:  > 20% annual volatility
        
        PURE CLASSIFICATION - no threshold changes to logic
        """
        if volatility_percent <= 12:
            return "LOW"
        elif volatility_percent <= 20:
            return "NORMAL"
        else:
            return "ELEVATED"
    
    @staticmethod
    def get_risk_narrative(risk_context, volatility_percent, signal_type):
        """Generate human-readable risk context explanation."""
        narratives = {
            "LOW": f"Low volatility ({volatility_percent:.1f}%) - stable price action, reduced swing risk",
            "NORMAL": f"Normal volatility ({volatility_percent:.1f}%) - acceptable price swings, standard management required",
            "ELEVATED": f"Elevated volatility ({volatility_percent:.1f}%) - larger price swings, active monitoring needed"
        }
        return narratives.get(risk_context, "Unknown risk context")


class HOLDJustificationGenerator:
    """Generate explicit rationale for HOLD signals (informational only)."""
    
    @staticmethod
    def generate_hold_rationale(trend_percent, momentum_percent, volatility_percent):
        """
        Deterministic justification for HOLD signals.
        
        Rules:
        - Trend between -1% and +1%: Indecisive trend
        - Momentum between -1% and +2%: Mixed/weak momentum
        - No bullish/bearish conviction required
        
        PURELY TEMPLATE-BASED - no predictive language
        """
        reasons = []
        
        # Trend analysis
        if -1 <= trend_percent <= 1:
            reasons.append(f"Indecisive trend ({trend_percent:.2f}% vs 50-day MA) - insufficient directional bias")
        else:
            reasons.append(f"Weak trend momentum")
        
        # Momentum analysis
        if -1 <= momentum_percent <= 2:
            reasons.append(f"Mixed momentum ({momentum_percent:.2f}% in 10 days) - no clear directional conviction")
        else:
            reasons.append(f"Momentum does not justify entry/exit")
        
        # Volatility note
        vol_status = "high volatility" if volatility_percent > 20 else "moderate volatility" if volatility_percent > 12 else "low volatility"
        reasons.append(f"{vol_status} adds uncertainty")
        
        rationale = (
            f"HOLD recommended: "
            f"{'; '.join(reasons)}. "
            f"Re-evaluate when trend clarifies (>1%) or momentum strengthens (>2%). "
            f"Avoid forced entry/exit in unclear conditions."
        )
        
        return rationale


class Phase19_3_OutputEnhancer:
    """Main orchestrator for Phase 19.3 enhancements."""
    
    def __init__(self):
        self.buy_analyzer = BUYEntryQualityAnalyzer()
        self.risk_classifier = RiskContextClassifier()
        self.hold_generator = HOLDJustificationGenerator()
        self.enhancement_log = []
    
    def enhance_recommendation(self, rec):
        """
        Add Phase 19.3 metadata to a single recommendation.
        PRESERVES all Phase 19.2 data exactly.
        """
        enhanced = rec.copy()  # Keep all Phase 19.2 data
        
        # 1. BUY ENTRY QUALITY (BUY only)
        if rec.get('signal') == 'BUY':
            buy_low = rec.get('buy_range_low')
            buy_high = rec.get('buy_range_high')
            
            if buy_low and buy_high:
                enhanced['Entry_Quality'] = self.buy_analyzer.calculate_entry_zones(buy_low, buy_high)
        
        # 2. RISK CONTEXT (ALL signals)
        volatility = rec.get('volatility', 0)
        risk_context = self.risk_classifier.classify_risk_context(volatility)
        enhanced['Risk_Context'] = risk_context
        enhanced['Risk_Context_Narrative'] = self.risk_classifier.get_risk_narrative(
            risk_context, volatility, rec.get('signal')
        )
        
        # 3. HOLD JUSTIFICATION (HOLD only)
        if rec.get('signal') == 'HOLD':
            trend = rec.get('trend', 0)
            momentum = rec.get('momentum', 0)
            
            enhanced['Hold_Rationale'] = self.hold_generator.generate_hold_rationale(
                trend, momentum, volatility
            )
        
        return enhanced
    
    def enhance_json_output(self, json_data):
        """Enhance Phase 19.2 JSON output with Phase 19.3 metadata."""
        enhanced_data = json_data.copy()
        
        # Enhance all recommendations
        enhanced_recommendations = []
        for rec in json_data.get('recommendations', []):
            enhanced_rec = self.enhance_recommendation(rec)
            enhanced_recommendations.append(enhanced_rec)
        
        enhanced_data['recommendations'] = enhanced_recommendations
        
        # Update metadata
        if 'metadata' not in enhanced_data:
            enhanced_data['metadata'] = {}
        
        enhanced_data['metadata']['phase_19_3_enhanced'] = True
        enhanced_data['metadata']['enhancement_timestamp'] = datetime.now().isoformat()
        enhanced_data['metadata']['enhancements'] = {
            'buy_entry_zones': 'Added (Optimal/Extended)',
            'risk_context': 'Added (LOW/NORMAL/ELEVATED)',
            'hold_justification': 'Added (Explicit rationale)'
        }
        
        return enhanced_data
    
    def load_and_enhance_json(self, json_file_path):
        """Load Phase 19.2 JSON and apply Phase 19.3 enhancements."""
        with open(json_file_path, 'r') as f:
            phase_19_2_data = json.load(f)
        
        return self.enhance_json_output(phase_19_2_data)
    
    def save_enhanced_json(self, enhanced_data, output_path):
        """Save enhanced JSON with _ENHANCED suffix."""
        with open(output_path, 'w') as f:
            json.dump(enhanced_data, f, indent=2)
        
        return output_path


def verify_signal_counts_identical(original_data, enhanced_data):
    """
    VALIDATION: Prove signal counts are identical.
    This is the critical test - enhancement must not change counts.
    """
    original_recs = original_data.get('recommendations', [])
    enhanced_recs = enhanced_data.get('recommendations', [])
    
    if len(original_recs) != len(enhanced_recs):
        return False, f"Count mismatch: {len(original_recs)} vs {len(enhanced_recs)}"
    
    # Count by signal type
    orig_signals = {}
    enh_signals = {}
    
    for rec in original_recs:
        signal = rec.get('signal')
        orig_signals[signal] = orig_signals.get(signal, 0) + 1
    
    for rec in enhanced_recs:
        signal = rec.get('signal')
        enh_signals[signal] = enh_signals.get(signal, 0) + 1
    
    if orig_signals != enh_signals:
        return False, f"Signal mismatch: {orig_signals} vs {enh_signals}"
    
    return True, f"VERIFIED: Signal counts identical - {orig_signals}"


def verify_core_fields_unchanged(original_rec, enhanced_rec):
    """
    VALIDATION: Prove core trading fields are unchanged.
    """
    critical_fields = [
        'symbol', 'signal', 'score', 'current_price',
        'buy_range_low', 'buy_range_high', 'stop_loss',
        'target_1', 'target_2', 'rr_ratio',
        'trend', 'momentum', 'volatility', 'analysis'
    ]
    
    for field in critical_fields:
        orig_val = original_rec.get(field)
        enh_val = enhanced_rec.get(field)
        
        if orig_val != enh_val:
            return False, f"Field {field} changed: {orig_val} -> {enh_val}"
    
    return True, "All critical fields unchanged"


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("PHASE 19.3: OUTPUT CLARITY ENHANCER")
        print("Usage: python phase19_3_output_clarity_enhancer.py <input_json_path>")
        print("\nExample:")
        print("  python phase19_3_output_clarity_enhancer.py nifty50_analysis/NIFTY50_ANALYSIS_20260112_154916.json")
        sys.exit(1)
    
    input_json = sys.argv[1]
    
    # Verify file exists
    if not Path(input_json).exists():
        print(f"ERROR: File not found: {input_json}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("PHASE 19.3: OUTPUT CLARITY ENHANCEMENT")
    print("="*70)
    
    # Load original
    print("\n[1] Loading Phase 19.2 output...")
    with open(input_json, 'r') as f:
        original_data = json.load(f)
    print(f"    ✓ Loaded {len(original_data.get('recommendations', []))} recommendations")
    
    # Enhance
    print("\n[2] Applying Phase 19.3 enhancements...")
    enhancer = Phase19_3_OutputEnhancer()
    enhanced_data = enhancer.enhance_json_output(original_data)
    print("    ✓ Added BUY entry zones")
    print("    ✓ Added risk context tags")
    print("    ✓ Added HOLD justifications")
    
    # Validate counts
    print("\n[3] Validating signal counts...")
    counts_valid, counts_msg = verify_signal_counts_identical(original_data, enhanced_data)
    if counts_valid:
        print(f"    ✓ {counts_msg}")
    else:
        print(f"    ❌ {counts_msg}")
        sys.exit(1)
    
    # Validate core fields
    print("\n[4] Validating core fields unchanged...")
    all_fields_valid = True
    for orig, enh in zip(
        original_data.get('recommendations', [])[:3],
        enhanced_data.get('recommendations', [])[:3]
    ):
        fields_valid, fields_msg = verify_core_fields_unchanged(orig, enh)
        if not fields_valid:
            print(f"    ❌ {orig.get('symbol')}: {fields_msg}")
            all_fields_valid = False
    
    if all_fields_valid:
        print("    ✓ All core fields unchanged (sampled 3 records)")
    else:
        print("    ❌ Core field validation failed")
        sys.exit(1)
    
    # Save enhanced
    output_json = input_json.replace('.json', '_ENHANCED.json')
    print(f"\n[5] Saving enhanced output...")
    enhancer.save_enhanced_json(enhanced_data, output_json)
    print(f"    ✓ Saved: {output_json}")
    
    # Show sample
    print("\n[6] Sample enhancements:")
    for rec in enhanced_data.get('recommendations', [])[:2]:
        print(f"\n    {rec.get('symbol')} ({rec.get('signal')})")
        print(f"      Risk Context: {rec.get('Risk_Context')}")
        if 'Entry_Quality' in rec:
            eo = rec['Entry_Quality']['Optimal_Entry_Zone']
            print(f"      Optimal Entry: {eo['Range_Low']} - {eo['Range_High']}")
        if 'Hold_Rationale' in rec:
            print(f"      Hold Reason: {rec['Hold_Rationale'][:70]}...")
    
    print("\n" + "="*70)
    print("✅ PHASE 19.3 ENHANCEMENT COMPLETE")
    print("="*70)
