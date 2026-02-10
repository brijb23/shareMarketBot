#!/usr/bin/env python3
"""
Pre-deployment verification script
Checks if everything is configured correctly before pushing to GitHub
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if Path(dirpath).exists() and Path(dirpath).is_dir():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}")
        return True
    except ImportError as e:
        print(f"❌ {description} - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("PRE-DEPLOYMENT VERIFICATION")
    print("=" * 60)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # Check core files
    print("📁 Checking Core Files...")
    total_checks += 1
    checks_passed += check_file_exists("dashboard.py", "Dashboard script")
    
    total_checks += 1
    checks_passed += check_file_exists("nifty50_weekly_automation.py", "Standard analysis script")
    
    total_checks += 1
    checks_passed += check_file_exists("nifty50_weekly_automation_enhanced.py", "Enhanced analysis script")
    
    total_checks += 1
    checks_passed += check_file_exists("nifty50_weekly_integrated_analysis.py", "Integrated analysis script")
    
    total_checks += 1
    checks_passed += check_file_exists("requirements.txt", "Requirements file")
    
    print()
    
    # Check GitHub Actions workflows
    print("🤖 Checking GitHub Actions Workflows...")
    total_checks += 1
    checks_passed += check_file_exists(".github/workflows/daily_analysis.yml", "Daily analysis workflow")
    
    total_checks += 1
    checks_passed += check_file_exists(".github/workflows/manual_analysis.yml", "Manual trigger workflow")
    
    print()
    
    # Check stock universe
    print("📊 Checking Stock Universe Configuration...")
    total_checks += 1
    checks_passed += check_file_exists("universes/stock_universe.py", "Stock universe file")
    
    # Test import
    total_checks += 1
    if check_import("universes.stock_universe", "Stock universe import"):
        checks_passed += 1
        try:
            from universes.stock_universe import get_stock_universe, get_stock_count
            count = get_stock_count()
            print(f"   📈 {count} stocks configured")
        except Exception as e:
            print(f"   ⚠️  Warning: {str(e)}")
    
    print()
    
    # Check directories
    print("📂 Checking Directory Structure...")
    total_checks += 1
    checks_passed += check_directory_exists("src", "Source modules directory")
    
    total_checks += 1
    checks_passed += check_directory_exists("nifty50_analysis", "Analysis output directory")
    
    total_checks += 1
    checks_passed += check_directory_exists("data", "Data directory")
    
    total_checks += 1
    checks_passed += check_directory_exists("logs", "Logs directory")
    
    print()
    
    # Check documentation
    print("📚 Checking Documentation...")
    total_checks += 1
    checks_passed += check_file_exists("README.md", "Main README")
    
    total_checks += 1
    checks_passed += check_file_exists("DEPLOYMENT_GUIDE.md", "Deployment guide")
    
    total_checks += 1
    checks_passed += check_file_exists(".gitignore", "Git ignore file")
    
    print()
    
    # Check key dependencies
    print("📦 Checking Key Dependencies...")
    dependencies = [
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("yfinance", "yfinance"),
        ("streamlit", "Streamlit")
    ]
    
    for module, name in dependencies:
        total_checks += 1
        checks_passed += check_import(module, f"{name} package")
    
    print()
    print("=" * 60)
    print(f"RESULTS: {checks_passed}/{total_checks} checks passed")
    print("=" * 60)
    
    if checks_passed == total_checks:
        print()
        print("🎉 ALL CHECKS PASSED!")
        print()
        print("✅ Your project is ready for deployment!")
        print()
        print("Next steps:")
        print("1. git add .")
        print("2. git commit -m 'Initial commit with automation'")
        print("3. git push origin main")
        print("4. Deploy to Streamlit Cloud")
        print()
        print("See DEPLOYMENT_GUIDE.md for detailed instructions.")
        return 0
    else:
        print()
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Create missing directories manually")
        print("- Verify all files are in correct locations")
        return 1

if __name__ == "__main__":
    sys.exit(main())
