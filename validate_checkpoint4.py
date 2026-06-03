#!/usr/bin/env python3
"""
Checkpoint Validation for Volatile Newsletter & Content Generation System
Validates that content is being generated and stored correctly.
"""

import os
import yaml
import glob
from datetime import datetime

CONTENT_BASE_PATH = "/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/content/"
NEWSLETTERS_PATH = os.path.join(CONTENT_BASE_PATH, "newsletters/")
REPORTS_PATH = os.path.join(CONTENT_BASE_PATH, "reports/")
SOCIAL_PATH = os.path.join(CONTENT_BASE_PATH, "social/")

def validate_content_generation():
    """Validate that content generation system is working correctly."""
    print("=== Volatile Newsletter & Content Generation System Checkpoint ===")
    print(f"Validating content in: {CONTENT_BASE_PATH}")
    print()
    
    # Check if content directory exists
    if not os.path.exists(CONTENT_BASE_PATH):
        print("❌ FAIL: Content directory does not exist")
        return False
    
    # Check subdirectories
    newsletters_exist = os.path.exists(NEWSLETTERS_PATH)
    reports_exist = os.path.exists(REPORTS_PATH)
    social_exist = os.path.exists(SOCIAL_PATH)
    
    print(f"Newsletters directory: {'✅ EXISTS' if newsletters_exist else '❌ MISSING'}")
    print(f"Reports directory: {'✅ EXISTS' if reports_exist else '❌ MISSING'}")
    print(f"Social directory: {'✅ EXISTS' if social_exist else '❌ MISSING'}")
    
    if not (newsletters_exist and reports_exist and social_exist):
        print("❌ FAIL: Missing content directories")
        return False
    
    # Count files in each directory
    newsletter_files = glob.glob(os.path.join(NEWSLETTERS_PATH, "*.md"))
    report_files = glob.glob(os.path.join(REPORTS_PATH, "*.md"))
    social_files = glob.glob(os.path.join(SOCIAL_PATH, "*.md"))
    market_summary_files = glob.glob(os.path.join(CONTENT_BASE_PATH, "market_*.md"))
    
    print(f"\nFile Counts:")
    print(f"  Newsletters: {len(newsletter_files)}")
    print(f"  Reports: {len(report_files)}")
    print(f"  Social alerts: {len(social_files)}")
    print(f"  Market summaries: {len(market_summary_files)}")
    
    # Validate newsletter files
    newsletter_validation = []
    for filepath in newsletter_files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for frontmatter
            if not content.startswith('---'):
                newsletter_validation.append((filename, False, "Missing frontmatter"))
                continue
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                newsletter_validation.append((filename, False, "Invalid frontmatter format"))
                continue
            
            frontmatter = yaml.safe_load(parts[1].strip()) or {}
            
            # Check required fields for newsletter
            required_fields = ['title', 'type', 'generated_at']
            missing_fields = [field for field in required_fields if field not in frontmatter]
            if missing_fields:
                newsletter_validation.append((filename, False, f"Missing fields: {missing_fields}"))
                continue
            
            # Check type
            if frontmatter.get('type') != 'newsletter':
                newsletter_validation.append((filename, False, f"Incorrect type: {frontmatter.get('type')}"))
                continue
            
            # Check for content
            if len(parts[2].strip()) < 50:
                newsletter_validation.append((filename, False, "Content too small"))
                continue
            
            newsletter_validation.append((filename, True, f"OK - Type: {frontmatter.get('type')}, Generated: {frontmatter.get('generated_at', 'unknown')[:10]}"))
            
        except Exception as e:
            newsletter_validation.append((filename, False, f"Parse error: {e}"))
    
    # Validate report files
    report_validation = []
    for filepath in report_files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            if not content.startswith('---'):
                report_validation.append((filename, False, "Missing frontmatter"))
                continue
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                report_validation.append((filename, False, "Invalid frontmatter format"))
                continue
            
            frontmatter = yaml.safe_load(parts[1].strip()) or {}
            
            if frontmatter.get('type') != 'report':
                report_validation.append((filename, False, f"Incorrect type: {frontmatter.get('type')}"))
                continue
            
            if len(parts[2].strip()) < 50:
                report_validation.append((filename, False, "Content too small"))
                continue
            
            report_validation.append((filename, True, f"OK - Type: {frontmatter.get('type')}, Generated: {frontmatter.get('generated_at', 'unknown')[:10]}"))
            
        except Exception as e:
            report_validation.append((filename, False, f"Parse error: {e}"))
    
    # Validate social alert files
    social_validation = []
    for filepath in social_files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            if not content.startswith('---'):
                social_validation.append((filename, False, "Missing frontmatter"))
                continue
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                social_validation.append((filename, False, "Invalid frontmatter format"))
                continue
            
            frontmatter = yaml.safe_load(parts[1].strip()) or {}
            
            # Social alerts could be type signal_alert or social
            content_type = frontmatter.get('type', '')
            if content_type not in ['signal_alert', 'social']:
                social_validation.append((filename, False, f"Unexpected type: {content_type}"))
                continue
            
            if len(parts[2].strip()) < 20:
                social_validation.append((filename, False, "Content too small"))
                continue
            
            social_validation.append((filename, True, f"OK - Type: {content_type}, Generated: {frontmatter.get('generated_at', 'unknown')[:10]}"))
            
        except Exception as e:
            social_validation.append((filename, False, f"Parse error: {e}"))
    
    # Validate market summary files
    summary_validation = []
    for filepath in market_summary_files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            if not content.startswith('---'):
                summary_validation.append((filename, False, "Missing frontmatter"))
                continue
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                summary_validation.append((filename, False, "Invalid frontmatter format"))
                continue
            
            frontmatter = yaml.safe_load(parts[1].strip()) or {}
            
            if frontmatter.get('type') != 'summary':
                summary_validation.append((filename, False, f"Incorrect type: {frontmatter.get('type')}"))
                continue
            
            if len(parts[2].strip()) < 30:
                summary_validation.append((filename, False, "Content too small"))
                continue
            
            summary_validation.append((filename, True, f"OK - Type: {frontmatter.get('type')}, Generated: {frontmatter.get('generated_at', 'unknown')[:10]}"))
            
        except Exception as e:
            summary_validation.append((filename, False, f"Parse error: {e}"))
    
    # Print results
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    all_passed = True
    
    sections = [
        ("Newsletters", newsletter_validation),
        ("Reports", report_validation),
        ("Social Alerts", social_validation),
        ("Market Summaries", summary_validation)
    ]
    
    for section_name, validation_list in sections:
        print(f"\n{section_name}:")
        print("-" * 40)
        if not validation_list:
            print("  ⚠️  No files found")
            continue
            
        passed_count = sum(1 for _, passed, _ in validation_list if passed)
        total_count = len(validation_list)
        
        for filename, passed, message in validation_list:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} {filename:<35} {message}")
            if not passed:
                all_passed = False
        
        print(f"  Summary: {passed_count}/{total_count} passed")
    
    print("\n" + "="*80)
    
    # Overall result
    total_files = len(newsletter_files) + len(report_files) + len(social_files) + len(market_summary_files)
    
    if all_passed and total_files > 0:
        print("🎉 CHECKPOINT PASSED: Content generation system is working correctly!")
        print(f"✅ Generated {len(newsletter_files)} newsletters")
        print(f"✅ Generated {len(report_files)} reports")
        print(f"✅ Generated {len(social_files)} social alerts/signal alerts")
        print(f"✅ Generated {len(market_summary_files)} market summaries")
        print("✅ All content files have proper frontmatter and sufficient content")
        print("✅ Ready to proceed to Phase 3 (Community Intelligence) or enhance existing features")
        return True
    elif total_files == 0:
        print("💥 CHECKPOINT FAILED: No content files generated")
        return False
    else:
        print("💥 CHECKPOINT FAILED: Validation errors found in content files")
        return False

if __name__ == "__main__":
    success = validate_content_generation()
    exit(0 if success else 1)