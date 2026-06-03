#!/usr/bin/env python3
"""
Batch Signal Generation for all Volatile symbols
"""

import os
import sys
sys.path.append('/mnt/c/CreedAI/volatile_dev')

from signal_generator import SignalGenerator

def main():
    """Generate and save signals for all symbols."""
    print("Batch Signal Generation")
    print("=" * 50)
    
    generator = SignalGenerator()
    
    # List of symbols to process
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 
               'bitcoin', 'ethereum', 'binancecoin',
               'EUR-USD', 'GBP-USD', 'USD-JPY']
    
    success_count = 0
    fail_count = 0
    
    for symbol in symbols:
        print(f"\nProcessing {symbol}...")
        
        # Generate signal
        signal = generator.generate_composite_signal(symbol)
        
        print(f"  Signal: {signal['signal']} (Strength: {signal['strength']}%, Confidence: {signal['confidence']}%)")
        
        # Save to vault
        success = generator.save_signal_to_vault(signal)
        
        if success:
            print(f"  ✅ Saved signal for {symbol}")
            success_count += 1
        else:
            print(f"  ❌ Failed to save signal for {symbol}")
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