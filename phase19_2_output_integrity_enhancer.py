"""
PHASE 19.2: OUTPUT INTEGRITY ENHANCER
=====================================

Purpose:
- Fix direction-aware risk & R:R calculation integrity
- Enforce narrative coherence between signal direction and explanation text
- Validate and correct invalid risk values
- Ensure SELL explanations justify SELL signal
- Ensure BUY explanations justify BUY signal

OUTPUT LAYER ONLY - No decision logic modifications
"""

import json
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime


class RiskIntegrityValidator:
    """Validates and corrects risk calculations for direction awareness."""
    
    @staticmethod
    def validate_risk_calculation(
        signal: str,
        entry_price: float,
        stop_loss: float,
        target_price: float
    ) -> Tuple[float, float, float, bool]:
        """
        Calculate direction-aware risk and R:R ratio.
        
        Args:
            signal: "BUY" or "SELL"
            entry_price: Current price (entry point)
            stop_loss: Stop loss price
            target_price: Target price
            
        Returns:
            (risk, reward, rr_ratio, is_valid)
            
        Rules:
            - For BUY:
                risk = abs(entry_price - stop_loss)
                reward = abs(target_price - entry_price)
            - For SELL:
                risk = abs(stop_loss - entry_price)
                reward = abs(entry_price - target_price)
            - Risk must ALWAYS be > 0
            - R:R must be mathematically valid
        """
        try:
            if signal.upper() == "BUY":
                risk = abs(entry_price - stop_loss)
                reward = abs(target_price - entry_price)
            elif signal.upper() == "SELL":
                # For SELL: risk is the distance above entry to stop_loss
                # reward is distance below entry to target
                risk = abs(stop_loss - entry_price)
                reward = abs(entry_price - target_price)
            else:
                return 0, 0, 0, False
            
            # Validate: risk must be positive
            if risk <= 0:
                return 0, 0, 0, False
            
            # Calculate R:R ratio
            rr_ratio = reward / risk if risk > 0 else 0
            
            return risk, reward, rr_ratio, True
            
        except (TypeError, ZeroDivisionError):
            return 0, 0, 0, False
    
    @staticmethod
    def format_rr_display(rr_ratio: float) -> str:
        """Format R:R ratio for display (e.g., 1.50:1)."""
        if rr_ratio == 0 or not isinstance(rr_ratio, (int, float)):
            return "INVALID"
        try:
            return f"{rr_ratio:.2f}:1"
        except:
            return "INVALID"


class NarrativeCoherenceValidator:
    """Validates and corrects narrative coherence between signal and explanation."""
    
    # Bullish descriptors that should NOT appear in SELL explanations
    BULLISH_DESCRIPTORS = [
        r'\bpositive\s+momentum\b',
        r'\bgood\s+momentum\b',
        r'\bgood\s+strength\b',
        r'\bstrong\s+uptrend\b',
        r'\bupward\s+pressure\b',
        r'\bpositive\s+trend\b',
        r'\bgaining\s+strength\b',
        r'\baccelerat\w+\s+upward\b',
        r'\brally\b.*\bstrength\b',
        r'\bbuying\s+pressure\b',
        r'\bpositive\s+divergence\b',
        r'\bgain\b.*\bmomentum\b',
        r'\bupside\s+break\b',
        r'\bstrong\s+recovery\b',
    ]
    
    # Bearish descriptors that should NOT appear unqualified in BUY explanations
    BEARISH_DESCRIPTORS = [
        r'\bweak\s+downtrend\b',
        r'\bdowntrend\b',
        r'\bnegative\s+momentum\b',
        r'\bweak\s+momentum\b',
        r'\bselling\s+pressure\b',
        r'\bnegative\s+trend\b',
        r'\blosing\s+strength\b',
        r'\bdownward\b',
        r'\bcollapse\b',
        r'\bcrash\b',
    ]
    
    @staticmethod
    def detect_bullish_language(text: str) -> List[str]:
        """Detect bullish descriptors in text."""
        matches = []
        for pattern in NarrativeCoherenceValidator.BULLISH_DESCRIPTORS:
            if re.search(pattern, text, re.IGNORECASE):
                match = re.search(pattern, text, re.IGNORECASE).group(0)
                matches.append(match)
        return matches
    
    @staticmethod
    def detect_bearish_language(text: str) -> List[str]:
        """Detect bearish descriptors in text."""
        matches = []
        for pattern in NarrativeCoherenceValidator.BEARISH_DESCRIPTORS:
            if re.search(pattern, text, re.IGNORECASE):
                match = re.search(pattern, text, re.IGNORECASE).group(0)
                matches.append(match)
        return matches
    
    @staticmethod
    def reframe_text(
        text: str,
        signal: str,
        issue_descriptors: List[str]
    ) -> str:
        """
        Reframe text to enforce narrative coherence.
        
        Strategy:
        1. For SELL with bullish language: contextualize within downtrend
        2. For BUY with bearish language: explain as temporary weakness
        3. Always maintain clarity of the signal
        """
        
        if signal.upper() == "SELL":
            # Reframe bullish language in SELL context
            text = re.sub(
                r'\bpositive\s+momentum\b',
                'short-term positive momentum within broader weakness',
                text,
                flags=re.IGNORECASE
            )
            text = re.sub(
                r'\bgood\s+momentum\b',
                'temporary momentum bounce',
                text,
                flags=re.IGNORECASE
            )
            text = re.sub(
                r'\bgood\s+strength\b',
                'temporary strength recovery',
                text,
                flags=re.IGNORECASE
            )
            text = re.sub(
                r'\bbuying\s+pressure\b',
                'temporary buying pressure',
                text,
                flags=re.IGNORECASE
            )
            
            # Ensure SELL justification in final sentence
            if not re.search(r'(SELL|downtrend|weakness|avoid)\b', text[-100:], re.IGNORECASE):
                text = text.rstrip('.') + ". SELL signal justified by downtrend and risk/reward ratio."
        
        elif signal.upper() == "BUY":
            # Reframe bearish language in BUY context
            text = re.sub(
                r'\bweak\s+downtrend\b',
                'mild downtrend being challenged by uptrend',
                text,
                flags=re.IGNORECASE
            )
            text = re.sub(
                r'\bnegative\s+momentum\b',
                'negative momentum offset by strong price action',
                text,
                flags=re.IGNORECASE
            )
            
            # Ensure BUY justification in final sentence
            if not re.search(r'(BUY|uptrend|strength|opportunity)\b', text[-100:], re.IGNORECASE):
                text = text.rstrip('.') + ". BUY signal justified by uptrend and positive risk/reward."
        
        return text
    
    @staticmethod
    def validate_coherence(signal: str, explanation: str) -> Tuple[bool, List[str]]:
        """
        Check if signal and explanation are coherent.
        
        Returns:
            (is_coherent, issues_found)
        """
        issues = []
        
        if signal.upper() == "SELL":
            bullish_detected = NarrativeCoherenceValidator.detect_bullish_language(explanation)
            if bullish_detected:
                issues.append(f"Bullish language in SELL signal: {', '.join(set(bullish_detected))}")
        
        elif signal.upper() == "BUY":
            bearish_detected = NarrativeCoherenceValidator.detect_bearish_language(explanation)
            if bearish_detected:
                # BUY can have some bearish context, only flag if dominant
                if len(bearish_detected) > 1:
                    issues.append(f"Multiple bearish descriptors in BUY signal: {', '.join(set(bearish_detected))}")
        
        is_coherent = len(issues) == 0
        return is_coherent, issues


class OutputIntegrityEnhancer:
    """Main orchestrator for output integrity enhancement."""
    
    def __init__(self):
        self.risk_validator = RiskIntegrityValidator()
        self.narrative_validator = NarrativeCoherenceValidator()
        self.corrections_log = []
    
    def enhance_recommendation_dict(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a single recommendation dictionary with integrity checks.
        
        Args:
            rec: Recommendation dict with signal, entry, stop_loss, target, explanation
            
        Returns:
            Enhanced dict with corrected risk/RR and coherent narrative
        """
        signal = rec.get('signal', 'HOLD').upper()
        current_price = float(rec.get('current_price', 0))
        stop_loss = float(rec.get('stop_loss', 0))
        target_1 = float(rec.get('target_1', 0))
        
        # --- PART A: DIRECTION-AWARE RISK CALCULATION ---
        risk, reward, rr_ratio, is_valid = self.risk_validator.validate_risk_calculation(
            signal=signal,
            entry_price=current_price,
            stop_loss=stop_loss,
            target_price=target_1
        )
        
        if not is_valid:
            self.corrections_log.append({
                'symbol': rec.get('symbol', 'UNKNOWN'),
                'signal': signal,
                'issue': 'Invalid risk calculation',
                'before': f"Risk={rec.get('risk_amount', 'N/A')}, RR={rec.get('rr_ratio_1', 'N/A')}",
                'after': f"Risk={risk:.2f}, RR={self.risk_validator.format_rr_display(rr_ratio)}"
            })
        
        rec['risk_amount_corrected'] = risk
        rec['reward_amount_1'] = reward
        rec['rr_ratio_1_corrected'] = self.risk_validator.format_rr_display(rr_ratio)
        
        # --- PART B: NARRATIVE COHERENCE ENFORCEMENT ---
        explanation = rec.get('analysis', '')
        
        is_coherent, issues = self.narrative_validator.validate_coherence(
            signal=signal,
            explanation=explanation
        )
        
        if not is_coherent:
            # Reframe the explanation
            reframed = self.narrative_validator.reframe_text(
                text=explanation,
                signal=signal,
                issue_descriptors=[issue for issue in issues]
            )
            
            self.corrections_log.append({
                'symbol': rec.get('symbol', 'UNKNOWN'),
                'signal': signal,
                'issue': 'Narrative coherence violation',
                'details': issues,
                'before': explanation[:100] + '...' if len(explanation) > 100 else explanation,
                'after': reframed[:100] + '...' if len(reframed) > 100 else reframed
            })
            
            rec['analysis_corrected'] = reframed
        else:
            rec['analysis_corrected'] = explanation
        
        rec['coherence_valid'] = is_coherent
        
        return rec
    
    def validate_batch(self, recommendations: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate and enhance a batch of recommendations.
        
        Returns:
            (all_valid, validation_report)
        """
        validation_report = {
            'total_recommendations': len(recommendations),
            'total_corrections': len(self.corrections_log),
            'invalid_risk_values': [],
            'incoherent_narratives': [],
            'negative_risks': [],
            'zero_rr_ratios': [],
            'all_enhanced_records': []
        }
        
        for rec in recommendations:
            enhanced = self.enhance_recommendation_dict(rec)
            validation_report['all_enhanced_records'].append(enhanced)
            
            # Check for specific issues
            if enhanced.get('risk_amount_corrected', 0) < 0:
                validation_report['negative_risks'].append(enhanced.get('symbol'))
            
            if enhanced.get('rr_ratio_1_corrected') == '0.00:1':
                validation_report['zero_rr_ratios'].append(enhanced.get('symbol'))
            
            if not enhanced.get('coherence_valid', True):
                validation_report['incoherent_narratives'].append(enhanced.get('symbol'))
        
        all_valid = (
            len(validation_report['negative_risks']) == 0 and
            len(validation_report['zero_rr_ratios']) == 0 and
            len(validation_report['incoherent_narratives']) == 0
        )
        
        return all_valid, validation_report
    
    def generate_integrity_report(self) -> str:
        """Generate human-readable integrity validation report."""
        report = "PHASE 19.2 - OUTPUT INTEGRITY VALIDATION REPORT\n"
        report += "=" * 60 + "\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}\n\n"
        
        report += "CORRECTIONS APPLIED:\n"
        report += "-" * 60 + "\n"
        
        if not self.corrections_log:
            report += "✓ No corrections needed - all outputs valid\n"
        else:
            for i, correction in enumerate(self.corrections_log, 1):
                report += f"\n{i}. {correction.get('symbol', 'UNKNOWN')} ({correction.get('signal')})\n"
                report += f"   Issue: {correction.get('issue')}\n"
                if 'details' in correction:
                    report += f"   Details: {correction.get('details')}\n"
                report += f"   Before: {correction.get('before')}\n"
                report += f"   After: {correction.get('after')}\n"
        
        report += "\n" + "=" * 60 + "\n"
        report += f"Total Corrections: {len(self.corrections_log)}\n"
        
        return report


# Test function for validation
def test_integrity_enhancer():
    """Quick test of the enhancer."""
    enhancer = OutputIntegrityEnhancer()
    
    # Test case 1: SELL with invalid risk
    test_sell = {
        'symbol': 'TEST.NS',
        'signal': 'SELL',
        'current_price': 100,
        'stop_loss': 110,  # Above current - invalid for SELL entry
        'target_1': 90,
        'risk_amount': -10,  # Invalid negative
        'rr_ratio_1': '0.00:1',  # Invalid zero
        'analysis': 'SELL Signal: positive momentum remains strong with good strength'
    }
    
    # Test case 2: BUY normal
    test_buy = {
        'symbol': 'TEST2.NS',
        'signal': 'BUY',
        'current_price': 100,
        'stop_loss': 95,
        'target_1': 110,
        'risk_amount': 5,
        'rr_ratio_1': '2.00:1',
        'analysis': 'BUY Signal: strong uptrend above 50-day MA'
    }
    
    enhanced_sell = enhancer.enhance_recommendation_dict(test_sell)
    enhanced_buy = enhancer.enhance_recommendation_dict(test_buy)
    
    print("Enhanced SELL:", enhanced_sell)
    print("\nEnhanced BUY:", enhanced_buy)
    print("\nCorrection Log:", enhancer.corrections_log)
    print("\nIntegrity Report:\n", enhancer.generate_integrity_report())


if __name__ == "__main__":
    test_integrity_enhancer()
