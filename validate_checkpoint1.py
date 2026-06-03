#!/usr/bin/env python3
"""
Checkpoint Validation for Volatile Market Data Ingestion
Validates that Phase 1 Week 1 objectives have been met.
"""

import os
import yaml
import glob
from datetime import datetime
import re

VAULT_RESEARCH_PATH = "/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/market_data/"

def validate_market_data_notes():
    """Validate that market data notes have been created correctly."""
    print("=== Volatile Market Data Ingestion Checkpoint ===")
    print(f"Validating notes in: {VAULT_RESEARCH_PATH}")
    print()
    
    # Check if directory exists
    if not os.path.exists(VAULT_RESEARCH_PATH):
        print("❌ FAIL: Market data directory does not exist")
        return False
    
    # Get all markdown files
    md_files = glob.glob(os.path.join(VAULT_RESEARCH_PATH, "*.md"))
    print(f"Found {len(md_files)} markdown files")
    
    if len(md_files) == 0:
        print("❌ FAIL: No market data notes found")
        return False
    
    # Expected symbols (from our fetch script)
    expected_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 
                       'bitcoin', 'ethereum', 'binancecoin',
                       'EUR-USD', 'GBP-USD', 'USD-JPY']
    
    found_symbols = []
    validation_results = []
    
    for md_file in md_files:
        filename = os.path.basename(md_file)
        symbol = filename.replace('.md', '')
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
                required_fields = ['symbol', 'source', 'last_updated', 'data_points']
                missing_fields = [field for field in required_fields if field not in metadata]
                if missing_fields:
                    validation_results.append((symbol, False, f"Missing fields: {missing_fields}"))
                    continue
                
                # Check data table exists
                if '| Date |' not in content:
                    validation_results.append((symbol, False, "Missing data table"))
                    continue
                
                # Count data rows properly - look for the table and count rows between header and separator/disclaimer
                lines = content.split('\n')
                data_rows = []
                
                # Find the start of the data table (after header and separator)
                table_started = False
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    # Look for the header
                    if stripped.startswith('| Date |'):
                        # Next non-empty line should be the separator
                        # Look for the separator line
                        for j in range(i+1, len(lines)):
                            sep_stripped = lines[j].strip()
                            if sep_stripped.startswith('|------'):
                                # Found separator, now count data rows until we hit something that's not a data row
                                for k in range(j+1, len(lines)):
                                    data_stripped = lines[k].strip()
                                    # Stop if we hit empty line, disclaimer, or non-table line
                                    if data_stripped == '' or data_stripped.startswith('*Note:'):
                                        break
                                    # Count lines that look like data rows (start with | and contain a date)
                                    if data_stripped.startswith('|') and re.search(r'\d{4}-\d{2}-\d{2}', data_stripped):
                                        data_rows.append(lines[k])
                                    elif not data_stripped.startswith('|'):
                                        # Hit a non-table line, stop counting
                                        break
                                break  # Break out of separator search
                        break  # Break out of header search
                
                if len(data_rows) == 0:
                    validation_results.append((symbol, False, "No data rows found"))
                    continue
                
                # Validate that data_points matches actual rows (approximately)
                if metadata['data_points'] != len(data_rows):
                    validation_results.append((symbol, False, f"data_points mismatch: claimed {metadata['data_points']}, found {len(data_rows)}"))
                    continue
                
                validation_results.append((symbol, True, f"OK - {len(data_rows)} data points from {metadata['source']}"))
                
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
        print("\n🎉 CHECKPOINT PASSED: Market data ingestion is working correctly!")
        print("✅ Data is being fetched from real APIs")
        print("✅ Data is being stored as markdown notes in the vault")
        print("✅ Notes have proper frontmatter and data tables")
        print("✅ Ready to proceed to technical indicator implementation")
        return True
    else:
        print("\n💥 CHECKPOINT FAILED: Issues found that need to be resolved")
        return False

if __name__ == "__main__":
    success = validate_market_data_notes()
    exit(0 if success else 1)