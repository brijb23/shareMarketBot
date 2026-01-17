"""
Sector Context Analyzer
Analyzes sector trends to adjust stock signals
"""

class SectorAnalyzer:
    """Analyze sector conditions to contextualize stock signals"""
    
    # Stock to sector mapping for NIFTY 50
    STOCK_SECTOR_MAP = {
        # Metals & Mining
        'TATASTEEL.NS': 'metals',
        'HINDCOA.NS': 'metals',
        'JSWSTEEL.NS': 'metals',
        'VEDL.NS': 'metals',
        'SAIL.NS': 'metals',
        'NATIONALAL.NS': 'metals',
        
        # Infrastructure
        'HCC.NS': 'infrastructure',
        'HUDCO.NS': 'infrastructure',
        'NTPC.NS': 'infrastructure',
        'POWERGRID.NS': 'infrastructure',
        'ONGC.NS': 'infrastructure',
        'COAL.NS': 'infrastructure',
        
        # IT
        'TCS.NS': 'it',
        'INFY.NS': 'it',
        'WIPRO.NS': 'it',
        'HCLTECH.NS': 'it',
        'TECHM.NS': 'it',
        'MPHASIS.NS': 'it',
        
        # Auto
        'MARUTI.NS': 'auto',
        'BHARATPE.NS': 'auto',
        'BAJAJFINSV.NS': 'auto',
        'EICHERMOT.NS': 'auto',
        'TATAMOTOR.NS': 'auto',
        'M&M.NS': 'auto',
        'HEROMOTOCO.NS': 'auto',
        
        # Banking
        'SBIN.NS': 'banking',
        'HDFC.NS': 'banking',
        'HDFC2.NS': 'banking',
        'HDFC3.NS': 'banking',
        'ICICIBANK.NS': 'banking',
        'KOTAKBANK.NS': 'banking',
        'HDFCBANK.NS': 'banking',
        'INDUSIND.NS': 'banking',
        'AXISBANK.NS': 'banking',
        
        # Consumer
        'HINDUNILVR.NS': 'consumer',
        'ITC.NS': 'consumer',
        'NESTLEIND.NS': 'consumer',
        'SUNPHARMA.NS': 'consumer',
        'BRITANNIA.NS': 'consumer',
        'MARICO.NS': 'consumer',
        'COLPAL.NS': 'consumer',
        'PGHH.NS': 'consumer',
        'DIVISLAB.NS': 'consumer',
        'CIPLA.NS': 'consumer',
        'PHARMALAB.NS': 'consumer',
        'BIOCON.NS': 'consumer',
        
        # Finance
        'BAJAJFINSV.NS': 'finance',
        'RELIANCE.NS': 'energy',
        'ABIRTEL.NS': 'telecom',
        'JIOTOWER.NS': 'telecom',
        'ADANIPORTS.NS': 'energy',
        
        # Cement
        'SHREECEM.NS': 'cement',
        'ADANICEMENT.NS': 'cement',
        'GRASIM.NS': 'cement',
        'ACC.NS': 'cement',
        
        # Automobile parts
        'MRF.NS': 'auto',
        'BOSCHIND.NS': 'auto',
    }
    
    # Sector health tracking (to be updated based on broader market context)
    SECTOR_CONTEXT = {
        'metals': {'trend': 'mixed', 'recovery_signal': 'improving'},      # Government support, cyclical
        'infrastructure': {'trend': 'mixed', 'recovery_signal': 'recovering'},  # Policy-driven
        'it': {'trend': 'stable', 'recovery_signal': 'none'},                   # Always stable
        'auto': {'trend': 'recovering', 'recovery_signal': 'growing'},          # Post-COVID growth
        'banking': {'trend': 'improving', 'recovery_signal': 'none'},           # Rate cycle dependent
        'consumer': {'trend': 'stable', 'recovery_signal': 'none'},             # Defensive
        'energy': {'trend': 'improving', 'recovery_signal': 'none'},            # Oil-dependent
        'telecom': {'trend': 'stable', 'recovery_signal': 'none'},              # Consolidated
        'cement': {'trend': 'improving', 'recovery_signal': 'growing'},         # Infrastructure dependent
        'finance': {'trend': 'improving', 'recovery_signal': 'none'},           # NBFCs growing
    }
    
    @staticmethod
    def get_stock_sector(symbol):
        """Get sector for a stock symbol"""
        return SectorAnalyzer.STOCK_SECTOR_MAP.get(symbol, 'other')
    
    @staticmethod
    def get_sector_context(symbol):
        """Get sector context for a stock"""
        sector = SectorAnalyzer.get_stock_sector(symbol)
        return SectorAnalyzer.SECTOR_CONTEXT.get(sector, {
            'trend': 'unknown',
            'recovery_signal': 'none'
        })
    
    @staticmethod
    def get_sector_adjustment(symbol, fundamental_score, technical_score, momentum_score):
        """
        Adjust signal based on sector context
        
        Returns: {'adjusted_signal': signal, 'reason': reason}
        """
        sector = SectorAnalyzer.get_stock_sector(symbol)
        context = SectorAnalyzer.get_sector_context(symbol)
        
        # Government/Infrastructure sector with recovery signals
        if sector in ['infrastructure', 'metals', 'energy']:
            # Check for convergence: If technical and momentum are rising while fund is low
            # This indicates institutional buying before fundamentals improve
            
            if (technical_score >= 65 and momentum_score >= 65 and 
                fundamental_score >= 50 and fundamental_score <= 60):
                
                return {
                    'adjustment': 1.2,  # Boost signal
                    'reason': f'Sector {sector} showing recovery: Strong technical + momentum despite moderate fundamentals'
                }
        
        # IT and consumer stocks should maintain strict fundamental requirements
        if sector in ['it', 'consumer']:
            if fundamental_score < 60:
                return {
                    'adjustment': 0.8,  # Lower signal strength
                    'reason': f'Sector {sector} requires strong fundamentals for signal quality'
                }
        
        # Auto sector in recovery phase
        if sector == 'auto' and context.get('recovery_signal') == 'growing':
            if technical_score >= 65 and momentum_score >= 60:
                return {
                    'adjustment': 1.15,
                    'reason': 'Auto sector in growth phase: Strong technicals + momentum detected'
                }
        
        return {
            'adjustment': 1.0,
            'reason': f'Sector {sector} context: No special adjustment'
        }
    
    @staticmethod
    def is_policy_sensitive_sector(symbol):
        """Check if sector is heavily dependent on government policy"""
        sector = SectorAnalyzer.get_stock_sector(symbol)
        return sector in ['infrastructure', 'energy', 'cement', 'telecom']
