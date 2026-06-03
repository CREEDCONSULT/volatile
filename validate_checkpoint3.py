#!/usr/bin/env python3
"""
Checkpoint Validation for Volatile Signal Generation Engine
Validates that signals are being generated and stored correctly.
"""

import os
import yaml
import glob
from datetime import datetime
import re

VAULT_SIGNALS_PATH = "/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/signals/"

def validate_signals():
    """Validate that signal notes have been created correctly."""
    print("=== Volatile Signal Generation Engine Checkpoint ===")
    print(f"Validating signal notes in: {VAULT_SIGNALS_PATH}")
    print()
    
    # Check if directory exists
    if not os.path.exists(VAULT_SIGNALS_PATH):
        print("❌ FAIL: Signals directory does not exist")
        return False
    
    # Get all markdown files
    md_files = glob.glob(os.path.join(VAULT_SIGNALS_PATH, "*.md"))
    print(f"Found {len(md_files)} signal markdown files")
    
    if len(md_files) == 0:
        print("❌ FAIL: No signal notes found")
        return False
    
    # Expected symbols (from our market data fetch)
    expected_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 
                       'bitcoin', 'ethereum', 'binancecoin',
                       'EUR-USD', 'GBP-USD', 'USD-JPY']
    
    found_symbols = []
    validation_results = []
    
    for md_file in md_files:
        filename = os.path.basename(md_file)
        # Remove _signal.md suffix
        symbol = filename.replace('_signal.md', '')
        found_symbols.append(symbol)
        
        try:
            with open(md_file, 'r') as f:
                content = f.read()
            
            # Check for frontmatter
            if not content.startswith('---'):
                validation_results.append((symbol, False, "Missing frontmatter"))
                continue
            
            # Try to parse frontmatter
            try:
                # Extract frontmatter (between first and second ---)
                parts = content.split('---', 2)
                if len(parts) < 3:
                    validation_results.append((symbol, False, "Invalid frontmatter format"))
                    continue
                
                frontmatter = parts[1].strip()
                metadata = yaml.safe_load(frontmatter)
                
                # Check required fields
                required_fields = ['symbol', 'signal', 'strength', 'confidence', 'timestamp']
                missing_fields = [field for field in required_fields if field not in metadata]
                if missing_fields:
                    validation_results.append((symbol, False, f"Missing fields: {missing_fields}"))
                    continue
                
                # Validate signal value
                if metadata['signal'] not in ['BUY', 'SELL', 'HOLD']:
                    validation_results.append((symbol, False, f"Invalid signal value: {metadata['signal']}"))
                    continue
                
                # Validate strength and confidence are numbers
                try:
                    strength = float(metadata['strength'])
                    confidence = float(metadata['confidence'])
                    if not (0 <= strength <= 100) or not (0 <= confidence <= 100):
                        validation_results.append((symbol, False, f"Strength or confidence out of range: {strength}, {confidence}"))
                        continue
                except ValueError:
                    validation_results.append((symbol, False, f"Strength or confidence not numeric: {metadata['strength']}, {metadata['confidence']}"))
                    continue
                
                # Check for content
                if len(content.strip()) < 100:  # Arbitrary minimum size
                    validation_results.append((symbol, False, "Content too small"))
                    continue
                
                validation_results.append((symbol, True, f"OK - Signal: {metadata['signal']}, Strength: {metadata['strength']}%, Confidence: {metadata['confidence']}%"))
                
            except yaml.YAMLError as e:
                validation_results.append((symbol, False, f"YAML parsing error: {e}"))
                continue
                
        except Exception as e:
            validation_results.append((symbol, False, f"File read error: {e}"))
            continue
    
    # Print results
    print("Validation Results:")
    print("-" * 80)
    all_passed = True
    
    for symbol, passed, message in validation_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {symbol:<12} {message}")
        if not passed:
            all_passed = False
    
    print("-" * 80)
    
    # Check if we found all expected symbols
    missing_symbols = set(expected_symbols) - set(found_symbols)
    extra_symbols = set(found_symbols) - set(expected_symbols)
    
    if missing_symbols:
        print(f"⚠️  WARNING: Missing expected symbols: {', '.join(sorted(missing_symbols))}")
    if extra_symbols:
        print(f"ℹ️  INFO: Found extra symbols: {', '.join(sorted(extra_symbols))}")
    
    # Final result
    if all_passed and len(missing_symbols) == 0:
        print("\n🎉 CHECKPOINT PASSED: Signal generation engine is working correctly!")
        print("✅ Signal notes are being generated for all symbols")
        print("✅ Notes have proper frontmatter with signal, strength, confidence")
        print("✅ Signals are BUY, SELL, or HOLD with valid percentages")
        print("✅ Ready to proceed to newsletter/content system or dashboard integration")
        return True
    else:
        print("\n💥 CHECKPOINT FAILED: Issues found that need to be resolved")
        return False

if __name__ == "__main__":
    success = validate_signals()
    exit(0 if success else 1)