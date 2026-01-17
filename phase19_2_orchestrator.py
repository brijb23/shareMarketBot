"""
PHASE 19.2 INTEGRATION WRAPPER
==============================

Applies Phase 19.2 integrity enhancements to existing recommendation outputs
while preserving all Phase 17-19 decision logic.
"""

import json
from typing import List, Dict, Any
from phase19_2_output_integrity_enhancer import OutputIntegrityEnhancer


class Phase19Point2Orchestrator:
    """Applies integrity enhancements to recommendation outputs."""
    
    def __init__(self):
        self.enhancer = OutputIntegrityEnhancer()
        self.results = None
    
    def process_json_recommendations(self, json_file_path: str) -> Dict[str, Any]:
        """
        Load recommendations from JSON and apply integrity enhancements.
        
        Args:
            json_file_path: Path to recommendations JSON file
            
        Returns:
            Dict with original and enhanced data
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both single list and dict containing list
            recs = data.get('recommendations', data) if isinstance(data, dict) else data
            
            if not isinstance(recs, list):
                recs = [data]
            
            # Apply enhancements to all recommendations
            enhanced_recs = []
            for rec in recs:
                enhanced = self.enhancer.enhance_recommendation_dict(rec)
                enhanced_recs.append(enhanced)
            
            # Validate batch
            all_valid, validation_report = self.enhancer.validate_batch(enhanced_recs)
            
            self.results = {
                'original_count': len(recs),
                'enhanced_count': len(enhanced_recs),
                'all_valid': all_valid,
                'corrections_applied': len(self.enhancer.corrections_log),
                'enhanced_recommendations': enhanced_recs,
                'validation_report': validation_report,
                'corrections_log': self.enhancer.corrections_log
            }
            
            return self.results
        
        except Exception as e:
            return {'error': str(e), 'file': json_file_path}
    
    def generate_report(self) -> str:
        """Generate comprehensive integrity report."""
        if not self.results:
            return "No analysis performed yet"
        
        report = "PHASE 19.2 - COMPREHENSIVE INTEGRITY REPORT\n"
        report += "=" * 80 + "\n\n"
        
        report += "SUMMARY\n"
        report += "-" * 80 + "\n"
        report += f"Original Recommendations: {self.results['original_count']}\n"
        report += f"Enhanced Recommendations: {self.results['enhanced_count']}\n"
        report += f"Corrections Applied: {self.results['corrections_applied']}\n"
        report += f"All Outputs Valid: {('[OK]' if self.results['all_valid'] else '[ISSUES]')}\n\n"
        
        report += "VALIDATION DETAILS\n"
        report += "-" * 80 + "\n"
        v_report = self.results['validation_report']
        report += f"Negative Risk Values Found: {len(v_report['negative_risks'])}\n"
        report += f"Zero R:R Ratios Found: {len(v_report['zero_rr_ratios'])}\n"
        report += f"Incoherent Narratives Found: {len(v_report['incoherent_narratives'])}\n\n"
        
        if v_report['negative_risks']:
            report += f"  Negative Risk Symbols: {', '.join(v_report['negative_risks'])}\n"
        if v_report['zero_rr_ratios']:
            report += f"  Zero R:R Symbols: {', '.join(v_report['zero_rr_ratios'])}\n"
        if v_report['incoherent_narratives']:
            report += f"  Incoherent Symbols: {', '.join(v_report['incoherent_narratives'])}\n"
        
        report += "\n" + self.enhancer.generate_integrity_report()
        
        return report


def main():
    """Test the orchestrator."""
    orchestrator = Phase19Point2Orchestrator()
    
    # Test with actual JSON output
    json_path = r"c:\PythonProjects\ShareMarketBot\nifty50_analysis\NIFTY50_DYNAMIC_20260112_151346.json"
    
    print("Loading and processing recommendations...")
    results = orchestrator.process_json_recommendations(json_path)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    print(orchestrator.generate_report())
    
    # Save enhanced recommendations
    enhanced_output = {
        'metadata': {
            'status': 'ENHANCED',
            'phase': '19.2',
            'total_enhanced': results['enhanced_count'],
            'corrections': results['corrections_applied']
        },
        'recommendations': results['enhanced_recommendations']
    }
    
    output_path = r"c:\PythonProjects\ShareMarketBot\nifty50_analysis\NIFTY50_DYNAMIC_ENHANCED_20260112_151346.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Enhanced recommendations saved to: {output_path}")


if __name__ == "__main__":
    main()
