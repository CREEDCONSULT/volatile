#!/usr/bin/env python3
"""
Technical Indicator Library for Volatile Platform
Calculates common trading indicators from market data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import yaml
import os
import re
from datetime import datetime

class TechnicalIndicatorCalculator:
    """Calculate technical indicators from market data."""
    
    @staticmethod
    def load_market_data_from_vault(symbol: str, vault_path: str = "/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/market_data/") -> Optional[pd.DataFrame]:
        """Load market data from a vault markdown note and convert to DataFrame."""
        filepath = os.path.join(vault_path, f"{symbol.replace('/', '-')}.md")
        
        if not os.path.exists(filepath):
            print(f"Market data file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract frontmatter
            if not content.startswith('---'):
                print(f"No frontmatter found in {filepath}")
                return None
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                print(f"Invalid frontmatter format in {filepath}")
                return None
            
            frontmatter = parts[1].strip()
            metadata = yaml.safe_load(frontmatter)
            
            # Extract data table
            lines = content.split('\n')
            data_lines = []
            
            # Find table start
            table_started = False
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('| Date |'):
                    table_started = True
                    continue
                elif table_started and stripped.startswith('|------'):
                    continue  # Skip separator
                elif table_started:
                    if stripped == '' or stripped.startswith('*Note:'):
                        break  # End of data
                    if stripped.startswith('|') and re.search(r'\d{4}-\d{2}-\d{2}', stripped):
                        data_lines.append(line)
            
            if not data_lines:
                print(f"No data lines found in {filepath}")
                return None
            
            # Parse data lines into DataFrame
            data_rows = []
            for line in data_lines:
                # Split by | and remove empty first/last elements
                parts = [part.strip() for part in line.split('|')[1:-1]]
                if len(parts) >= 6:  # Date, Open, High, Low, Close, Volume
                    try:
                        row = {
                            'Date': parts[0],
                            'Open': float(parts[1]),
                            'High': float(parts[2]),
                            'Low': float(parts[3]),
                            'Close': float(parts[4]),
                            'Volume': float(parts[5]) if parts[5] else 0.0
                        }
                        data_rows.append(row)
                    except ValueError as e:
                        print(f"Error parsing row {line}: {e}")
                        continue
            
            if not data_rows:
                print(f"No valid data rows found in {filepath}")
                return None
            
            df = pd.DataFrame(data_rows)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"Error loading market data from {filepath}: {e}")
            return None
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        if 'Close' not in df.columns or len(df) < period + 1:
            return pd.Series([np.nan] * len(df), index=df.index)
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        if 'Close' not in df.columns or len(df) < slow:
            return {
                'MACD': pd.Series([np.nan] * len(df), index=df.index),
                'Signal': pd.Series([np.nan] * len(df), index=df.index),
                'Histogram': pd.Series([np.nan] * len(df), index=df.index)
            }
        
        ema_fast = df['Close'].ewm(span=fast).mean()
        ema_slow = df['Close'].ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        if 'Close' not in df.columns or len(df) < period:
            return {
                'Upper': pd.Series([np.nan] * len(df), index=df.index),
                'Middle': pd.Series([np.nan] * len(df), index=df.index),
                'Lower': pd.Series([np.nan] * len(df), index=df.index)
            }
        
        middle = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'Upper': upper,
            'Middle': middle,
            'Lower': lower
        }
    
    @staticmethod
    def calculate_moving_averages(df: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> Dict[str, pd.Series]:
        """Calculate simple moving averages for given periods."""
        result = {}
        if 'Close' not in df.columns:
            return {f'SMA_{p}': pd.Series([np.nan] * len(df), index=df.index) for p in periods}
        
        for period in periods:
            if len(df) >= period:
                result[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
            else:
                result[f'SMA_{period}'] = pd.Series([np.nan] * len(df), index=df.index)
        
        return result
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Dict[str, any]:
        """Calculate all available technical indicators."""
        if df is None or len(df) == 0:
            return {}
        
        indicators = {}
        
        # Add the original OHLCV data
        indicators['OHLCV'] = df
        
        # Calculate RSI
        indicators['RSI'] = TechnicalIndicatorCalculator.calculate_rsi(df)
        
        # Calculate MACD
        macd_data = TechnicalIndicatorCalculator.calculate_macd(df)
        indicators.update(macd_data)
        
        # Calculate Bollinger Bands
        bb_data = TechnicalIndicatorCalculator.calculate_bollinger_bands(df)
        indicators.update(bb_data)
        
        # Calculate Moving Averages
        ma_data = TechnicalIndicatorCalculator.calculate_moving_averages(df)
        indicators.update(ma_data)
        
        return indicators
    
    @staticmethod
    def save_indicators_to_vault(symbol: str, indicators: Dict[str, any], 
                                vault_path: str = "/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/indicators/") -> bool:
        """Save calculated indicators as markdown notes in the vault."""
        try:
            os.makedirs(vault_path, exist_ok=True)
            
            # Create a safe filename
            safe_filename = f"{symbol.replace('/', '-')}_indicators.md"
            filepath = os.path.join(vault_path, safe_filename)
            
            # Build markdown content
            md_content = f"""---
symbol: {symbol}
indicator_types: {list(indicators.keys())}
last_updated: {datetime.now().isoformat()}
data_points: {len(indicators.get('OHLCV', pd.DataFrame()))}
---

# Technical Indicators for {symbol}

*Last updated: {datetime.now().isoformat()}*
*Data points: {len(indicators.get('OHLCV', pd.DataFrame()))}*

## Overview

This note contains calculated technical indicators for {symbol} based on market data.

"""
            
            # Add each indicator section
            for indicator_name, indicator_data in indicators.items():
                if indicator_name == 'OHLCV':
                    continue  # Skip the raw data, we already have that
                
                md_content += f"### {indicator_name}\n\n"
                
                if isinstance(indicator_data, pd.Series):
                    # Create a table for the indicator values
                    md_content += f"| Date | {indicator_name} |\n|------|------------|\n"
                    
                    # Get corresponding dates from OHLCV data
                    ohlcv_df = indicators.get('OHLCV')
                    if ohlcv_df is not None and len(ohlcv_df) == len(indicator_data):
                        for i, (date, value) in enumerate(zip(ohlcv_df['Date'], indicator_data)):
                            date_str = date.strftime('%Y-%m-%d')
                            if pd.isna(value):
                                md_content += f"| {date_str} | N/A |\n"
                            else:
                                md_content += f"| {date_str} | {value:.4f} |\n"
                    else:
                        # Fallback if we don't have matching OHLCV data
                        for i, value in enumerate(indicator_data):
                            if pd.isna(value):
                                md_content += f"| Row {i} | N/A |\n"
                            else:
                                md_content += f"| Row {i} | {value:.4f} |\n"
                
                elif isinstance(indicator_data, dict):
                    # Handle nested dictionaries (like MACD with multiple lines)
                    for sub_name, sub_data in indicator_data.items():
                        if isinstance(sub_data, pd.Series):
                            md_content += f"#### {sub_name}\n\n"
                            md_content += f"| Date | {sub_name} |\n|------|------------|\n"
                            
                            ohlcv_df = indicators.get('OHLCV')
                            if ohlcv_df is not None and len(ohlcv_df) == len(sub_data):
                                for i, (date, value) in enumerate(zip(ohlcv_df['Date'], sub_data)):
                                    date_str = date.strftime('%Y-%m-%d')
                                    if pd.isna(value):
                                        md_content += f"| {date_str} | N/A |\n"
                                    else:
                                        md_content += f"| {date_str} | {value:.4f} |\n"
                            else:
                                for i, value in enumerate(sub_data):
                                    if pd.isna(value):
                                        md_content += f"| Row {i} | N/A |\n"
                                    else:
                                        md_content += f"| Row {i} | {value:.4f} |\n"
                            md_content += "\n"
                
                md_content += "\n"
            
            md_content += f"\n*Note: These indicators are for research purposes only and not financial advice.*\n"
            
            # Write to file
            with open(filepath, 'w') as f:
                f.write(md_content)
            
            print(f"Saved indicators for {symbol} to {filepath}")
            return True
            
        except Exception as e:
            print(f"Error saving indicators for {symbol}: {e}")
            return False

def main():
    """Main function to demonstrate technical indicator calculation."""
    print("Volatile Technical Indicator Calculator")
    print("=" * 50)
    
    # Test with one symbol first
    calculator = TechnicalIndicatorCalculator()
    
    # Load market data for AAPL
    print("\n1. Loading market data for AAPL...")
    df = calculator.load_market_data_from_vault("AAPL")
    
    if df is None:
        print("❌ Failed to load market data")
        return
    
    print(f"✅ Loaded {len(df)} data points")
    print(df.head())
    
    # Calculate all indicators
    print("\n2. Calculating technical indicators...")
    indicators = calculator.calculate_all_indicators(df)
    
    print(f"✅ Calculated indicators: {list(indicators.keys())}")
    
    # Show some sample values
    if 'RSI' in indicators:
        print(f"\n3. Sample RSI values:")
        rsi_series = indicators['RSI']
        for i in range(max(0, len(rsi_series)-3), len(rsi_series)):
            if not pd.isna(rsi_series.iloc[i]):
                date = df.iloc[i]['Date'].strftime('%Y-%m-%d')
                print(f"   {date}: {rsi_series.iloc[i]:.2f}")
    
    if 'MACD' in indicators:
        print(f"\n4. Sample MACD values:")
        macd_series = indicators['MACD']
        signal_series = indicators['Signal']
        for i in range(max(0, len(macd_series)-3), len(macd_series)):
            if not pd.isna(macd_series.iloc[i]):
                date = df.iloc[i]['Date'].strftime('%Y-%m-%d')
                print(f"   {date}: MACD={macd_series.iloc[i]:.4f}, Signal={signal_series.iloc[i]:.4f}")
    
    # Save indicators to vault
    print("\n5. Saving indicators to vault...")
    success = calculator.save_indicators_to_vault("AAPL", indicators)
    
    if success:
        print("✅ Indicators saved successfully")
    else:
        print("❌ Failed to save indicators")
    
    print("\n" + "=" * 50)
    print("Technical Indicator Calculator Demo Complete")

if __name__ == "__main__":
    main()