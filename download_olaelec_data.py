"""
OLAELEC DATA DOWNLOADER
Download historical price and fundamental data for OLA ELECTRIC
IPO Date: August 2024
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime

class OlaElecDataDownloader:
    def __init__(self):
        self.symbol = 'OLAELEC.NS'
        self.data_dir_prices = 'data/prices'
        self.data_dir_fundamentals = 'data/fundamentals'
        self.start_date = '2024-08-01'  # IPO was in August 2024
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        
    def download_price_data(self):
        """Download price data from yfinance"""
        print(f"Downloading price data for {self.symbol}...")
        print(f"Period: {self.start_date} to {self.end_date}\n")
        
        try:
            # Download price data
            df = yf.download(self.symbol, start=self.start_date, end=self.end_date, progress=False)
            
            if df.empty:
                print(f"[ERROR] No price data found for {self.symbol}")
                return False
            
            # Reset index to get date as column, then reset again
            df = df.reset_index()
            
            print(f"✓ Downloaded {len(df)} trading days of price data")
            print(f"  Date Range: {df['Date'].iloc[0].strftime('%Y-%m-%d')} to {df['Date'].iloc[-1].strftime('%Y-%m-%d')}")
            min_price = float(df['Close'].min())
            max_price = float(df['Close'].max())
            print(f"  Price Range: Rs {min_price:.2f} - Rs {max_price:.2f}\n")
            
            # Save to CSV
            filename = os.path.join(self.data_dir_prices, f'{self.symbol}.csv')
            df.to_csv(filename, index=False)
            print(f"✓ Saved price data to: {filename}\n")
            
            # Display sample
            print("Sample Data (Last 5 days):")
            print(df.tail().to_string(index=False))
            print()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to download price data: {e}\n")
            import traceback
            traceback.print_exc()
            return False
    
    def create_fundamental_data(self):
        """Create fundamental data file for OLAELEC"""
        print(f"\nCreating fundamental data for {self.symbol}...")
        
        # OLAELEC fundamental profile (based on public info)
        # This is template data - actual scoring will be done by main.py
        fundamental_data = {
            'Date': [self.end_date],
            'Symbol': [self.symbol],
            'Sector': ['Automobiles'],
            'Industry': ['Electric Vehicles'],
            'CompanyName': ['Ola Electric Mobility Limited'],
            'MarketCap': ['100000000000'],  # 1 Lakh Crore (approximate)
            'PE_Ratio': ['0'],  # Not profitable yet
            'PB_Ratio': ['0'],
            'ROE': ['0'],
            'ROA': ['0'],
            'Debt_to_Equity': ['0'],
            'Current_Ratio': ['0'],
            'Quick_Ratio': ['0'],
            'DebtToAssets': ['0'],
            'EPS': ['0'],
            'Revenue': ['0'],
            'NetIncome': ['0'],
            'Free_Cash_Flow': ['0'],
        }
        
        df = pd.DataFrame(fundamental_data)
        
        # Save to CSV
        filename = os.path.join(self.data_dir_fundamentals, f'{self.symbol}.csv')
        df.to_csv(filename, index=False)
        
        print(f"✓ Created fundamental data template: {filename}")
        print("  Note: Fundamental scoring will use yfinance data when available\n")
        
        return True
    
    def verify_installation(self):
        """Verify data files were created"""
        print("Verifying installation...\n")
        
        price_file = os.path.join(self.data_dir_prices, f'{self.symbol}.csv')
        fund_file = os.path.join(self.data_dir_fundamentals, f'{self.symbol}.csv')
        
        price_ok = os.path.exists(price_file)
        fund_ok = os.path.exists(fund_file)
        
        print(f"  Price Data File: {'✓ EXISTS' if price_ok else '✗ MISSING'}")
        print(f"  Fundamental Data File: {'✓ EXISTS' if fund_ok else '✗ MISSING'}\n")
        
        if price_ok and fund_ok:
            price_df = pd.read_csv(price_file)
            print(f"  Price Data Records: {len(price_df)}")
            if 'Date' in price_df.columns:
                print(f"  Date Range: {price_df['Date'].iloc[0]} to {price_df['Date'].iloc[-1]}\n")
            return True
        
        return False
    
    def run(self):
        """Run complete download process"""
        print("="*100)
        print("OLA ELECTRIC (OLAELEC.NS) DATA DOWNLOADER")
        print("="*100)
        print(f"\nTarget Symbol: {self.symbol}")
        print(f"IPO Date: August 2024")
        print(f"Download Period: {self.start_date} to {self.end_date}\n")
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir_prices, exist_ok=True)
        os.makedirs(self.data_dir_fundamentals, exist_ok=True)
        
        # Download data
        price_ok = self.download_price_data()
        fund_ok = self.create_fundamental_data()
        
        # Verify
        if price_ok and fund_ok:
            self.verify_installation()
            print("="*100)
            print("DOWNLOAD COMPLETE!")
            print("="*100)
            print("\nYou can now run analysis for OLAELEC.NS using:")
            print(f"  python main.py --mode snapshot --symbol {self.symbol} --as-of {self.end_date}")
            print(f"  python olaelect_today_analysis.py")
            print("\n✓ OLAELEC data is ready for analysis!")
            return True
        else:
            print("\n[ERROR] Download incomplete. Please check the errors above.")
            return False

def main():
    downloader = OlaElecDataDownloader()
    downloader.run()

if __name__ == "__main__":
    main()
