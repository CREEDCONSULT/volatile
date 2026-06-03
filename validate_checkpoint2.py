#!/usr/bin/env python3
"""
Checkpoint Validation for Volatile Technical Indicator Library
Validates that technical indicators are being calculated and stored correctly.
"""

import os
import yaml
import glob
from datetime import datetime
import re

VAULT_INDICATORS_PATH = "/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/indicators/"

def validate_technical_indicators():
    """Validate that technical indicator notes have been created correctly."""
    print("=== Volatile Technical Indicator Library Checkpoint ===")
    print(f"Validating indicator notes in: {VAULT_INDICATORS_PATH}")
    print()
    
    # Check if directory exists
    if not os.path.exists(VAULT_INDICATORS_PATH):
        print("❌ FAIL: Indicators directory does not exist")
        return False
    
    # Get all markdown files
    md_files = glob.glob(os.path.join(VAULT_INDICATORS_PATH, "*.md"))
    print(f"Found {len(md_files)} indicator markdown files")
    
    if len(md_files) == 0:
        print("❌ FAIL: No indicator notes found")
        return False
    
    # Expected symbols (from our market data fetch)
    expected_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 
                       'bitcoin', 'ethereum', 'binancecoin',
                       'EUR-USD', 'GBP-USD', 'USD-JPY']
    
    found_symbols = []
    validation_results = []
    
    for md_file in md_files:
        filename = os.path.basename(md_file)
        # Remove _indicators.md suffix
        symbol = filename.replace('_indicators.md', '')
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
                required_fields = ['symbol', 'indicator_types', 'last_updated', 'data_points']
                missing_fields = [field for field in required_fields if field not in metadata]
                if missing_fields:
                    validation_results.append((symbol, False, f"Missing fields: {missing_fields}"))
                    continue
                
                # Check that we have some indicator types
                if not metadata['indicator_types'] or len(metadata['indicator_types']) == 0:
                    validation_results.append((symbol, False, "No indicator types listed"))
                    continue
                
                # Check for data table or content
                if len(content.strip()) < 100:  # Arbitrary minimum size
                    validation_results.append((symbol, False, "Content too small"))
                    continue
                
                validation_results.append((symbol, True, f"OK - {len(metadata['indicator_types'])} indicator types, {metadata['data_points']} data points"))
                
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
        print("\n🎉 CHECKPOINT PASSED: Technical indicator library is working correctly!")
        print("✅ Indicator notes are being generated for all symbols")
        print("✅ Notes have proper frontmatter and content")
        print("✅ Ready to proceed to signal generation engine")
        return True
    else:
        print("\n💥 CHECKPOINT FAILED: Issues found that need to be resolved")
        return False

if __name__ == "__main__":
    success = validate_technical_indicators()
    exit(0 if success else 1)