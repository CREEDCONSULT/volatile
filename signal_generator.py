#!/usr/bin/env python3
"""
Signal Generation Engine for Volatile Platform
Generates trading signals based on technical indicators and market data.
"""

import os
import sys
sys.path.append('/mnt/c/CreedAI/volatile_dev')

from technical_indicators import TechnicalIndicatorCalculator
import yaml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class SignalGenerator:
    """Generate trading signals based on technical analysis."""
    
    def __init__(self, vault_base_path: str = "/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/"):
        self.vault_base_path = vault_base_path
        self.market_data_path = os.path.join(vault_base_path, "market_data/")
        self.indicators_path = os.path.join(vault_base_path, "indicators/")
        self.signals_path = os.path.join(vault_base_path, "signals/")
        self.calculator = TechnicalIndicatorCalculator()
        
        # Ensure signals directory exists
        os.makedirs(self.signals_path, exist_ok=True)
    
    def load_market_data(self, symbol: str) -> pd.DataFrame:
        """Load market data from vault."""
        return self.calculator.load_market_data_from_vault(symbol, self.market_data_path)
    
    def load_indicators(self, symbol: str) -> dict:
        """Load pre-calculated indicators from vault."""
        indicator_file = os.path.join(self.indicators_path, f"{symbol.replace('/', '-')}_indicators.md")
        
        if not os.path.exists(indicator_file):
            return {}
        
        try:
            with open(indicator_file, 'r') as f:
                content = f.read()
            
            # Extract frontmatter
            if not content.startswith('---'):
                return {}
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}
            
            frontmatter = parts[1].strip()
            metadata = yaml.safe_load(frontmatter)
            
            # We would need to parse the actual indicator values from the tables
            # For now, we'll recalculate them (in a real system, we'd store them more efficiently)
            df = self.load_market_data(symbol)
            if df is None:
                return {}
            
            indicators = self.calculator.calculate_all_indicators(df)
            return indicators
            
        except Exception as e:
            print(f"Error loading indicators for {symbol}: {e}")
            return {}
    
    def generate_rsi_signal(self, rsi_series: pd.Series, 
                           oversold: int = 30, overbought: int = 70) -> dict:
        """Generate signal based on RSI."""
        if rsi_series is None or len(rsi_series) == 0:
            return {"signal": "HOLD", "strength": 0, "reason": "No RSI data"}
        
        latest_rsi = rsi_series.iloc[-1]
        
        if pd.isna(latest_rsi):
            return {"signal": "HOLD", "strength": 0, "reason": "RSI data unavailable"}
        
        if latest_rsi < oversold:
            # Oversold - potential buy signal
            strength = min(100, (oversold - latest_rsi) * 2)  # Scale strength
            return {
                "signal": "BUY",
                "strength": strength,
                "reason": f"RSI oversold at {latest_rsi:.1f}",
                "rsi_value": latest_rsi
            }
        elif latest_rsi > overbought:
            # Overbought - potential sell signal
            strength = min(100, (latest_rsi - overbought) * 2)
            return {
                "signal": "SELL",
                "strength": strength,
                "reason": f"RSI overbought at {latest_rsi:.1f}",
                "rsi_value": latest_rsi
            }
        else:
            # Neutral zone
            return {
                "signal": "HOLD",
                "strength": 50 - abs(latest_rsi - 50),  # Strength based on distance from 50
                "reason": f"RSI neutral at {latest_rsi:.1f}",
                "rsi_value": latest_rsi
            }
    
    def generate_macd_signal(self, macd_series: pd.Series, 
                            signal_series: pd.Series) -> dict:
        """Generate signal based on MACD crossover."""
        if macd_series is None or signal_series is None:
            return {"signal": "HOLD", "strength": 0, "reason": "No MACD data"}
        
        if len(macd_series) < 2 or len(signal_series) < 2:
            return {"signal": "HOLD", "strength": 0, "reason": "Insufficient MACD data"}
        
        # Get latest values
        latest_macd = macd_series.iloc[-1]
        latest_signal = signal_series.iloc[-1]
        prev_macd = macd_series.iloc[-2]
        prev_signal = signal_series.iloc[-2]
        
        if pd.isna(latest_macd) or pd.isna(latest_signal):
            return {"signal": "HOLD", "strength": 0, "reason": "MACD data unavailable"}
        
        # Check for crossover
        if prev_macd <= prev_signal and latest_macd > latest_signal:
            # Bullish crossover
            strength = min(100, abs(latest_macd - latest_signal) * 100)  # Scale appropriately
            return {
                "signal": "BUY",
                "strength": strength,
                "reason": "MACD bullish crossover",
                "macd_value": latest_macd,
                "signal_value": latest_signal
            }
        elif prev_macd >= prev_signal and latest_macd < latest_signal:
            # Bearish crossover
            strength = min(100, abs(latest_macd - latest_signal) * 100)
            return {
                "signal": "SELL",
                "strength": strength,
                "reason": "MACD bearish crossover",
                "macd_value": latest_macd,
                "signal_value": latest_signal
            }
        else:
            # No crossover
            return {
                "signal": "HOLD",
                "strength": 50,  # Neutral strength
                "reason": "MACD no crossover",
                "macd_value": latest_macd,
                "signal_value": latest_signal
            }
    
    def generate_bollinger_signal(self, close_series: pd.Series,
                                 upper_series: pd.Series,
                                 lower_series: pd.Series,
                                 middle_series: pd.Series) -> dict:
        """Generate signal based on Bollinger Bands position."""
        if any(s is None for s in [close_series, upper_series, lower_series, middle_series]):
            return {"signal": "HOLD", "strength": 0, "reason": "No Bollinger Bands data"}
        
        if len(close_series) == 0:
            return {"signal": "HOLD", "strength": 0, "reason": "No price data"}
        
        latest_close = close_series.iloc[-1]
        latest_upper = upper_series.iloc[-1]
        latest_lower = lower_series.iloc[-1]
        latest_middle = middle_series.iloc[-1]
        
        if any(pd.isna(val) for val in [latest_close, latest_upper, latest_lower, latest_middle]):
            return {"signal": "HOLD", "strength": 0, "reason": "Bollinger Bands data unavailable"}
        
        # Calculate position within bands (0 = at lower band, 1 = at upper band)
        band_width = latest_upper - latest_lower
        if band_width == 0:
            position = 0.5
        else:
            position = (latest_close - latest_lower) / band_width
        
        # Generate signals based on position
        if position < 0.1:  # Near or below lower band
            return {
                "signal": "BUY",
                "strength": min(100, (0.1 - position) * 1000),  # Strength increases as price goes lower
                "reason": f"Price near lower Bollinger Band (position: {position:.2f})",
                "price": latest_close,
                "lower_band": latest_lower,
                "upper_band": latest_upper
            }
        elif position > 0.9:  # Near or above upper band
            return {
                "signal": "SELL",
                "strength": min(100, (position - 0.9) * 1000),
                "reason": f"Price near upper Bollinger Band (position: {position:.2f})",
                "price": latest_close,
                "lower_band": latest_lower,
                "upper_band": latest_upper
            }
        else:
            # Within bands
            return {
                "signal": "HOLD",
                "strength": 50 - abs(position - 0.5) * 100,  # Stronger hold near middle
                "reason": f"Price within Bollinger Bands (position: {position:.2f})",
                "price": latest_close,
                "lower_band": latest_lower,
                "upper_band": latest_upper
            }
    
    def generate_moving_average_signal(self, close_series: pd.Series,
                                      sma_short: pd.Series,
                                      sma_long: pd.Series) -> dict:
        """Generate signal based on moving average crossover."""
        if any(s is None for s in [close_series, sma_short, sma_long]):
            return {"signal": "HOLD", "strength": 0, "reason": "No moving average data"}
        
        if len(close_series) < 2 or len(sma_short) < 2 or len(sma_long) < 2:
            return {"signal": "HOLD", "strength": 0, "reason": "Insufficient moving average data"}
        
        latest_close = close_series.iloc[-1]
        latest_sma_short = sma_short.iloc[-1]
        latest_sma_long = sma_long.iloc[-1]
        prev_sma_short = sma_short.iloc[-2]
        prev_sma_long = sma_long.iloc[-2]
        
        if any(pd.isna(val) for val in [latest_close, latest_sma_short, latest_sma_long,
                                       prev_sma_short, prev_sma_long]):
            return {"signal": "HOLD", "strength": 0, "reason": "Moving average data unavailable"}
        
        # Check for golden cross (short MA crosses above long MA)
        if prev_sma_short <= prev_sma_long and latest_sma_short > latest_sma_long:
            strength = min(100, abs(latest_sma_short - latest_sma_long) / latest_close * 1000)
            return {
                "signal": "BUY",
                "strength": strength,
                "reason": "Golden cross: short MA crossed above long MA",
                "price": latest_close,
                "sma_short": latest_sma_short,
                "sma_long": latest_sma_long
            }
        # Check for death cross (short MA crosses below long MA)
        elif prev_sma_short >= prev_sma_long and latest_sma_short < latest_sma_long:
            strength = min(100, abs(latest_sma_short - latest_sma_long) / latest_close * 1000)
            return {
                "signal": "SELL",
                "strength": strength,
                "reason": "Death cross: short MA crossed below long MA",
                "price": latest_close,
                "sma_short": latest_sma_short,
                "sma_long": latest_sma_long
            }
        else:
            # No cross - check if price is above/below MAs for trend strength
            if latest_close > latest_sma_short and latest_sma_short > latest_sma_long:
                # Strong uptrend
                strength = min(80, (latest_close - latest_sma_long) / latest_sma_long * 100)
                return {
                    "signal": "BUY",
                    "strength": strength,
                    "reason": "Strong uptrend: price above short MA above long MA",
                    "price": latest_close,
                    "sma_short": latest_sma_short,
                    "sma_long": latest_sma_long
                }
            elif latest_close < latest_sma_short and latest_sma_short < latest_sma_long:
                # Strong downtrend
                strength = min(80, (latest_sma_long - latest_close) / latest_sma_long * 100)
                return {
                    "signal": "SELL",
                    "strength": strength,
                    "reason": "Strong downtrend: price below short MA below long MA",
                    "price": latest_close,
                    "sma_short": latest_sma_short,
                    "sma_long": latest_sma_long
                }
            else:
                # Mixed or ranging
                return {
                    "signal": "HOLD",
                    "strength": 50,
                    "reason": "No clear MA trend",
                    "price": latest_close,
                    "sma_short": latest_sma_short,
                    "sma_long": latest_sma_long
                }
    
    def generate_composite_signal(self, symbol: str) -> dict:
        """Generate a composite signal from multiple indicators."""
        print(f"Generating composite signal for {symbol}...")
        
        # Load data and indicators
        df = self.load_market_data(symbol)
        if df is None:
            return {
                "symbol": symbol,
                "signal": "HOLD",
                "strength": 0,
                "confidence": 0,
                "reason": "Failed to load market data",
                "timestamp": datetime.now().isoformat()
            }
        
        indicators = self.load_indicators(symbol)
        if not indicators:
            # Calculate on the fly
            indicators = self.calculator.calculate_all_indicators(df)
        
        # Extract indicator series
        rsi = indicators.get('RSI')
        macd = indicators.get('MACD')
        macd_signal = indicators.get('Signal')
        bb_upper = indicators.get('Upper')
        bb_middle = indicators.get('Middle')
        bb_lower = indicators.get('Lower')
        close = df['Close'] if 'Close' in df.columns else None
        sma_20 = indicators.get('SMA_20')
        sma_50 = indicators.get('SMA_50')
        
        # Generate individual signals
        signals = []
        
        # RSI signal
        if rsi is not None:
            rsi_signal = self.generate_rsi_signal(rsi)
            signals.append(("RSI", rsi_signal))
        
        # MACD signal
        if macd is not None and macd_signal is not None:
            macd_signal_result = self.generate_macd_signal(macd, macd_signal)
            signals.append(("MACD", macd_signal_result))
        
        # Bollinger Bands signal
        if all(s is not None for s in [close, bb_upper, bb_middle, bb_lower]):
            bb_signal = self.generate_bollinger_signal(close, bb_upper, bb_lower, bb_middle)
            signals.append(("BB", bb_signal))
        
        # Moving Average signal
        if all(s is not None for s in [close, sma_20, sma_50]):
            ma_signal = self.generate_moving_average_signal(close, sma_20, sma_50)
            signals.append(("MA", ma_signal))
        
        # If we have no signals, return HOLD
        if not signals:
            return {
                "symbol": symbol,
                "signal": "HOLD",
                "strength": 0,
                "confidence": 0,
                "reason": "No indicators available for signal generation",
                "timestamp": datetime.now().isoformat()
            }
        
        # Combine signals using weighted voting
        buy_weight = 0
        sell_weight = 0
        hold_weight = 0
        total_weight = 0
        
        signal_details = []
        
        for indicator_name, signal_result in signals:
            signal = signal_result.get("signal", "HOLD")
            strength = signal_result.get("strength", 0)
            reason = signal_result.get("reason", "")
            
            # Weight the signal by its strength
            weight = strength / 100.0  # Normalize to 0-1
            
            if signal == "BUY":
                buy_weight += weight
            elif signal == "SELL":
                sell_weight += weight
            else:  # HOLD
                hold_weight += weight
            
            total_weight += weight
            
            signal_details.append({
                "indicator": indicator_name,
                "signal": signal,
                "strength": strength,
                "reason": reason,
                "weight": weight
            })
        
        # Determine final signal
        if total_weight == 0:
            final_signal = "HOLD"
            confidence = 0
        else:
            # Normalize weights
            buy_weight /= total_weight
            sell_weight /= total_weight
            hold_weight /= total_weight
            
            # Determine signal with highest weight
            if buy_weight > sell_weight and buy_weight > hold_weight:
                final_signal = "BUY"
                confidence = buy_weight * 100
            elif sell_weight > buy_weight and sell_weight > hold_weight:
                final_signal = "SELL"
                confidence = sell_weight * 100
            else:
                final_signal = "HOLD"
                confidence = hold_weight * 100
        
        # Calculate overall strength (average of individual signal strengths)
        if signals:
            avg_strength = sum(s[1]["strength"] for s in signals) / len(signals)
        else:
            avg_strength = 0
        
        # Prepare final signal object
        final_signal_obj = {
            "symbol": symbol,
            "signal": final_signal,
            "strength": round(avg_strength, 1),
            "confidence": round(confidence, 1),
            "reason": f"Composite signal from {len(signals)} indicators",
            "timestamp": datetime.now().isoformat(),
            "individual_signals": signal_details,
            "weights": {
                "buy": round(buy_weight * 100, 1) if total_weight > 0 else 0,
                "sell": round(sell_weight * 100, 1) if total_weight > 0 else 0,
                "hold": round(hold_weight * 100, 1) if total_weight > 0 else 0
            }
        }
        
        return final_signal_obj
    
    def save_signal_to_vault(self, signal: dict) -> bool:
        """Save signal as a markdown note in the vault."""
        try:
            symbol = signal["symbol"]
            safe_filename = f"{symbol.replace('/', '-')}_signal.md"
            filepath = os.path.join(self.signals_path, safe_filename)
            
            # Build markdown content
            md_content = f"""---
symbol: {symbol}
signal: {signal['signal']}
strength: {signal['strength']}
confidence: {signal['confidence']}
timestamp: {signal['timestamp']}
---

# Trading Signal for {symbol}

*Generated: {signal['timestamp']}*
*Signal: {signal['signal']}*
*Strength: {signal['strength']}%*
*Confidence: {signal['confidence']}%*

## Signal Summary

{signal['reason']}

## Individual Indicator Signals

| Indicator | Signal | Strength | Reason |
|-----------|--------|----------|--------|
"""
            
            for ind_signal in signal.get('individual_signals', []):
                md_content += f"| {ind_signal['indicator']} | {ind_signal['signal']} | {ind_signal['strength']}% | {ind_signal['reason']} |\n"
            
            md_content += f"""
## Signal Weights

- Buy Weight: {signal['weights']['buy']}%
- Sell Weight: {signal['weights']['sell']}%
- Hold Weight: {signal['weights']['hold']}%

## Trading Recommendation

Based on the analysis of {len(signal.get('individual_signals', []))} technical indicators, the recommended action for {symbol} is: **{signal['signal']}** with {signal['confidence']}% confidence.

*Note: This signal is for research purposes only and not financial advice. Always conduct your own research and consider your risk tolerance before making trading decisions.*
"""
            
            # Write to file
            with open(filepath, 'w') as f:
                f.write(md_content)
            
            print(f"Saved signal for {symbol} to {filepath}")
            return True
            
        except Exception as e:
            print(f"Error saving signal for {symbol}: {e}")
            return False

def main():
    """Main function to demonstrate signal generation."""
    print("Volatile Signal Generation Engine")
    print("=" * 50)
    
    # Initialize signal generator
    generator = SignalGenerator()
    
    # Test with one symbol first
    symbol = "AAPL"
    print(f"\nGenerating signal for {symbol}...")
    
    signal = generator.generate_composite_signal(symbol)
    
    print(f"Generated signal:")
    print(f"  Symbol: {signal['symbol']}")
    print(f"  Signal: {signal['signal']}")
    print(f"  Strength: {signal['strength']}%")
    print(f"  Confidence: {signal['confidence']}%")
    print(f"  Reason: {signal['reason']}")
    
    # Save signal to vault
    print(f"\nSaving signal to vault...")
    success = generator.save_signal_to_vault(signal)
    
    if success:
        print("✅ Signal saved successfully")
    else:
        print("❌ Failed to save signal")
    
    print("\n" + "=" * 50)
    print("Signal Generation Demo Complete")

if __name__ == "__main__":
    main()