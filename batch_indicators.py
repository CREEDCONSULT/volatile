#!/usr/bin/env python3
"""
Batch Technical Indicator Calculation for all Volatile symbols
"""

import os
import sys
sys.path.append('/mnt/c/CreedAI/volatile_dev')

from technical_indicators import TechnicalIndicatorCalculator

def main():
    """Calculate and save technical indicators for all symbols."""
    print("Batch Technical Indicator Calculation")
    print("=" * 50)
    
    calculator = TechnicalIndicatorCalculator()
    
    # List of symbols to process
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 
               'bitcoin', 'ethereum', 'binancecoin',
               'EUR-USD', 'GBP-USD', 'USD-JPY']
    
    success_count = 0
    fail_count = 0
    
    for symbol in symbols:
        print(f"\nProcessing {symbol}...")
        
        # Load market data
        df = calculator.load_market_data_from_vault(symbol)
        
        if df is None:
            print(f"  ❌ Failed to load market data for {symbol}")
            fail_count += 1
            continue
        
        print(f"  ✅ Loaded {len(df)} data points")
        
        # Calculate indicators
        indicators = calculator.calculate_all_indicators(df)
        print(f"  ✅ Calculated {len(indicators)} indicator types")
        
        # Save to vault
        success = calculator.save_indicators_to_vault(symbol, indicators)
        
        if success:
            print(f"  ✅ Saved indicators for {symbol}")
            success_count += 1
        else:
            print(f"  ❌ Failed to save indicators for {symbol}")
            fail_count += 1
    
    print("\n" + "=" * 50)
    print(f"Batch processing complete:")
    print(f"  ✅ Successful: {success_count}")
    print(f"  ❌ Failed: {fail_count}")
    
    if fail_count == 0:
        print("\n🎉 All symbols processed successfully!")
        return True
    else:
        print(f"\n⚠️  {fail_count} symbols failed to process")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)