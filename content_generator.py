#!/usr/bin/env python3
"""
Newsletter & Content Generation System for Volatile Platform
Generates trading newsletters, reports, and content from market data and signals.
"""

import os
import sys
sys.path.append('/mnt/c/CreedAI/volatile_dev')

import yaml
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import markdown
import hashlib

class ContentGenerator:
    """Generate various content types from Volatile platform data."""
    
    def __init__(self, vault_base_path: str = "/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/"):
        self.vault_base_path = vault_base_path
        self.market_data_path = os.path.join(vault_base_path, "market_data/")
        self.indicators_path = os.path.join(vault_base_path, "indicators/")
        self.signals_path = os.path.join(vault_base_path, "signals/")
        self.content_path = os.path.join(vault_base_path, "content/")
        self.newsletters_path = os.path.join(self.content_path, "newsletters/")
        self.reports_path = os.path.join(self.content_path, "reports/")
        self.social_path = os.path.join(self.content_path, "social/")
        
        # Ensure content directories exist
        os.makedirs(self.newsletters_path, exist_ok=True)
        os.makedirs(self.reports_path, exist_ok=True)
        os.makedirs(self.social_path, exist_ok=True)
        
        # Content templates
        self.templates = {
            "daily_newsletter": self._get_daily_newsletter_template(),
            "weekly_report": self._get_weekly_report_template(),
            "signal_alert": self._get_signal_alert_template(),
            "market_summary": self._get_market_summary_template(),
            "social_post": self._get_social_post_template()
        }
    
    def load_market_data(self, symbol: str) -> Dict[str, Any]:
        """Load market data for a symbol from vault."""
        filepath = os.path.join(self.market_data_path, f"{symbol.replace('/', '-')}.md")
        return self._parse_vault_note(filepath)
    
    def load_signal(self, symbol: str) -> Dict[str, Any]:
        """Load signal for a symbol from vault."""
        filepath = os.path.join(self.signals_path, f"{symbol.replace('/', '-')}_signal.md")
        return self._parse_vault_note(filepath)
    
    def load_indicators(self, symbol: str) -> Dict[str, Any]:
        """Load indicators for a symbol from vault."""
        filepath = os.path.join(self.indicators_path, f"{symbol.replace('/', '-')}_indicators.md")
        return self._parse_vault_note(filepath)
    
    def _parse_vault_note(self, filepath: str) -> Dict[str, Any]:
        """Parse a vault note and extract frontmatter and content."""
        if not os.path.exists(filepath):
            return {}
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract frontmatter
            if not content.startswith('---'):
                return {"content": content, "frontmatter": {}}
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {"content": content, "frontmatter": {}}
            
            frontmatter = yaml.safe_load(parts[1].strip()) or {}
            body_content = parts[2].strip()
            
            return {
                "frontmatter": frontmatter,
                "content": body_content,
                "full_content": content
            }
        except Exception as e:
            print(f"Error parsing vault note {filepath}: {e}")
            return {}
    
    def generate_daily_newsletter(self, date: datetime = None) -> Dict[str, Any]:
        """Generate a daily newsletter with top signals and market insights."""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        print(f"Generating daily newsletter for {date_str}...")
        
        # Get all signals for the day
        signals_data = self._get_all_signals()
        market_summary = self._get_market_overview()
        
        # Categorize signals
        buy_signals = [s for s in signals_data if s.get('signal') == 'BUY' and s.get('confidence', 0) > 60]
        sell_signals = [s for s in signals_data if s.get('signal') == 'SELL' and s.get('confidence', 0) > 60]
        hold_signals = [s for s in signals_data if s.get('signal') == 'HOLD']
        
        # Sort by confidence
        buy_signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        sell_signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        newsletter_data = {
            "date": date_str,
            "title": f"Volatile Daily Market Brief - {date_str}",
            "market_summary": market_summary,
            "top_buy_signals": buy_signals[:5],  # Top 5 BUY signals
            "top_sell_signals": sell_signals[:5],  # Top 5 SELL signals
            "signal_count": {
                "buy": len(buy_signals),
                "sell": len(sell_signals),
                "hold": len(hold_signals),
                "total": len(signals_data)
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate content using template
        content = self._render_template("daily_newsletter", newsletter_data)
        
        # Save to vault
        filepath = self._save_content(
            content, 
            newsletter_data, 
            "newsletter", 
            f"daily_{date_str}",
            self.newsletters_path
        )
        
        return {
            "type": "daily_newsletter",
            "filepath": filepath,
            "data": newsletter_data,
            "content_preview": content[:500] + "..." if len(content) > 500 else content
        }
    
    def generate_weekly_report(self, week_start: datetime = None) -> Dict[str, Any]:
        """Generate a weekly performance report."""
        if week_start is None:
            # Default to last Monday
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        week_str = week_start.strftime("%Y-%m-%d")
        print(f"Generating weekly report for week starting {week_str}...")
        
        # This would typically analyze performance over the week
        # For now, we'll create a summary based on current signals
        signals_data = self._get_all_signals()
        
        weekly_data = {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "title": f"Volatile Weekly Market Report - Week of {week_str}",
            "signal_performance": self._analyze_signal_performance(signals_data),
            "market_trends": self._identify_market_trends(),
            "top_movers": self._get_top_movers(),
            "generated_at": datetime.now().isoformat()
        }
        
        content = self._render_template("weekly_report", weekly_data)
        
        filepath = self._save_content(
            content,
            weekly_data,
            "report",
            f"weekly_{week_str}",
            self.reports_path
        )
        
        return {
            "type": "weekly_report",
            "filepath": filepath,
            "data": weekly_data,
            "content_preview": content[:500] + "..." if len(content) > 500 else content
        }
    
    def generate_signal_alert(self, symbol: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an alert for a significant signal."""
        print(f"Generating signal alert for {symbol}...")
        
        alert_data = {
            "symbol": symbol,
            "signal": signal_data.get('signal', 'HOLD'),
            "strength": signal_data.get('strength', 0),
            "confidence": signal_data.get('confidence', 0),
            "reason": signal_data.get('reason', 'No reason provided'),
            "timestamp": signal_data.get('timestamp', datetime.now().isoformat()),
            "alert_level": self._determine_alert_level(signal_data)
        }
        
        content = self._render_template("signal_alert", alert_data)
        
        # Save alert with timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_symbol = symbol.replace('/', '-')
        filename = f"alert_{safe_symbol}_{timestamp}.md"
        filepath = os.path.join(self.social_path, filename)
        
        # Add frontmatter
        frontmatter = {
            "symbol": symbol,
            "type": "signal_alert",
            "signal": alert_data['signal'],
            "confidence": alert_data['confidence'],
            "timestamp": alert_data['timestamp']
        }
        
        full_content = f"""---
{yaml.dump(frontmatter, default_flow_style=False)}---
{content}
"""
        
        with open(filepath, 'w') as f:
            f.write(full_content)
        
        print(f"Saved signal alert to {filepath}")
        
        return {
            "type": "signal_alert",
            "filepath": filepath,
            "data": alert_data,
            "content_preview": content[:300] + "..." if len(content) > 300 else content
        }
    
    def generate_market_summary(self) -> Dict[str, Any]:
        """Generate a general market summary."""
        print("Generating market summary...")
        
        signals_data = self._get_all_signals()
        
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "title": "Volatile Market Summary",
            "overview": self._get_market_overview(),
            "signal_distribution": self._get_signal_distribution(signals_data),
            "high_confidence_signals": [
                s for s in signals_data 
                if s.get('confidence', 0) > 70 and s.get('signal') in ['BUY', 'SELL']
            ],
            "market_breadth": self._calculate_market_breadth(signals_data)
        }
        
        content = self._render_template("market_summary", summary_data)
        
        filepath = self._save_content(
            content,
            summary_data,
            "summary",
            f"market_{datetime.now().strftime('%Y%m%d_%H%M')}",
            self.content_path
        )
        
        return {
            "type": "market_summary",
            "filepath": filepath,
            "data": summary_data,
            "content_preview": content[:500] + "..." if len(content) > 500 else content
        }
    
    def _get_all_signals(self) -> List[Dict[str, Any]]:
        """Load all signals from the vault."""
        signals = []
        if not os.path.exists(self.signals_path):
            return signals
        
        for filename in os.listdir(self.signals_path):
            if filename.endswith('_signal.md'):
                symbol = filename.replace('_signal.md', '').replace('-', '/')
                signal_data = self.load_signal(symbol)
                if signal_data and 'frontmatter' in signal_data:
                    frontmatter = signal_data['frontmatter']
                    signals.append({
                        "symbol": symbol,
                        "signal": frontmatter.get('signal', 'HOLD'),
                        "strength": float(frontmatter.get('strength', 0)),
                        "confidence": float(frontmatter.get('confidence', 0)),
                        "timestamp": frontmatter.get('timestamp', datetime.now().isoformat()),
                        "reason": f"Signal generated from technical analysis"
                    })
        return signals
    
    def _get_market_overview(self) -> Dict[str, Any]:
        """Get overall market overview."""
        signals = self._get_all_signals()
        
        if not signals:
            return {"status": "No data available"}
        
        buy_count = sum(1 for s in signals if s['signal'] == 'BUY')
        sell_count = sum(1 for s in signals if s['signal'] == 'SELL')
        hold_count = sum(1 for s in signals if s['signal'] == 'HOLD')
        total = len(signals)
        
        # Determine overall market bias
        if buy_count > sell_count * 1.5:
            bias = "Bullish"
        elif sell_count > buy_count * 1.5:
            bias = "Bearish"
        else:
            bias = "Neutral"
        
        avg_confidence = sum(s['confidence'] for s in signals) / total if total > 0 else 0
        
        return {
            "total_symbols": total,
            "buy_signals": buy_count,
            "sell_signals": sell_count,
            "hold_signals": hold_count,
            "market_bias": bias,
            "average_confidence": round(avg_confidence, 1)
        }
    
    def _determine_alert_level(self, signal_data: Dict[str, Any]) -> str:
        """Determine alert level based on signal strength and confidence."""
        confidence = signal_data.get('confidence', 0)
        strength = signal_data.get('strength', 0)
        
        # High confidence and strong signal
        if confidence > 80 and strength > 70:
            return "HIGH"
        # Moderate confidence or strength
        elif confidence > 60 or strength > 50:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _analyze_signal_performance(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze signal performance (placeholder for actual backtesting)."""
        # In a real system, this would compare signals to actual price movements
        # For now, we'll return basic stats
        buy_signals = [s for s in signals if s['signal'] == 'BUY']
        sell_signals = [s for s in signals if s['signal'] == 'SELL']
        
        return {
            "total_signals": len(signals),
            "buy_signals": len(buy_signals),
            "sell_signals": len(sell_signals),
            "avg_buy_confidence": round(sum(s['confidence'] for s in buy_signals) / max(len(buy_signals), 1), 1),
            "avg_sell_confidence": round(sum(s['confidence'] for s in sell_signals) / max(len(sell_signals), 1), 1),
            "high_confidence_signals": len([s for s in signals if s['confidence'] > 70])
        }
    
    def _identify_market_trends(self) -> List[str]:
        """Identify current market trends (placeholder)."""
        # This would analyze multiple timeframes, sectors, etc.
        return [
            "Mixed signals across asset classes",
            "Technology showing relative strength",
            "Forex pairs range-bound",
            "Crypto showing volatility contraction"
        ]
    
    def _get_top_movers(self) -> List[Dict[str, Any]]:
        """Get symbols with highest signal strength/confidence."""
        signals = self._get_all_signals()
        # Sort by combined strength and confidence
        signals_with_score = [
            {**s, "score": s.get('strength', 0) * s.get('confidence', 0) / 100}
            for s in signals
        ]
        signals_with_score.sort(key=lambda x: x['score'], reverse=True)
        return signals_with_score[:5]
    
    def _get_signal_distribution(self, signals: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of signal types."""
        distribution = {"BUY": 0, "SELL": 0, "HOLD": 0}
        for signal in signals:
            dist_signal = signal.get('signal', 'HOLD')
            if dist_signal in distribution:
                distribution[dist_signal] += 1
        return distribution
    
    def _calculate_market_breadth(self, signals: List[Dict[str, Any]]) -> float:
        """Calculate market breadth (% of bullish signals)."""
        if not signals:
            return 0.0
        bullish = sum(1 for s in signals if s['signal'] == 'BUY')
        return round((bullish / len(signals)) * 100, 1)
    
    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render a content template with data."""
        template = self.templates.get(template_name, "")
        if not template:
            return f"# Error: Template {template_name} not found\n\nData: {json.dumps(data, indent=2)}"
        
        # Simple template rendering - replace placeholders
        content = template
        for key, value in data.items():
            if isinstance(value, (str, int, float)):
                placeholder = f"{{{{{key}}}}}"
                content = content.replace(placeholder, str(value))
            elif isinstance(value, list):
                # Handle lists specially
                if key in ["top_buy_signals", "top_sell_signals", "high_confidence_signals"]:
                    list_content = ""
                    for item in value:
                        if isinstance(item, dict):
                            symbol = item.get('symbol', 'Unknown')
                            signal = item.get('signal', 'HOLD')
                            confidence = item.get('confidence', 0)
                            reason = item.get('reason', 'No reason')
                            list_content += f"- **{symbol}**: {signal} ({confidence}% confidence) - {reason}\n"
                        else:
                            list_content += f"- {item}\n"
                    placeholder = f"{{{{{key}}}}}"
                    content = content.replace(placeholder, list_content or "_No data_")
                elif key in ["market_trends"]:
                    list_content = "\n".join([f"- {trend}" for trend in value])
                    placeholder = f"{{{{{key}}}}}"
                    content = content.replace(placeholder, list_content or "_No trends identified_")
        
        # Handle nested objects for market_summary
        if "market_summary" in data and isinstance(data["market_summary"], dict):
            ms = data["market_summary"]
            for key, value in ms.items():
                placeholder = f"{{{{market_summary.{key}}}}}"
                content = content.replace(placeholder, str(value) if value is not None else "_N/A_")
        
        return content
    
    def _save_content(self, content: str, data: Dict[str, Any], 
                     content_type: str, filename_base: str, 
                     directory: str) -> str:
        """Save content to vault with frontmatter."""
        # Create filename
        safe_filename = f"{filename_base}.md"
        filepath = os.path.join(directory, safe_filename)
        
        # Prepare frontmatter
        frontmatter = {
            "title": data.get('title', f"{content_type.title()} - {filename_base}"),
            "type": content_type,
            "generated_at": data.get('generated_at', datetime.now().isoformat()),
            "symbols_covered": len(self._get_all_signals()) if content_type in ["newsletter", "report"] else 0
        }
        
        # Add type-specific fields
        if content_type == "newsletter":
            frontmatter.update({
                "date": data.get('date', ''),
                "signal_count": data.get('signal_count', {})
            })
        elif content_type == "report":
            frontmatter.update({
                "week_start": data.get('week_start', ''),
                "week_end": data.get('week_end', '')
            })
        
        # Create full content with frontmatter
        full_content = f"""---
{yaml.dump(frontmatter, default_flow_style=False)}---
{content}
"""
        
        # Write file
        with open(filepath, 'w') as f:
            f.write(full_content)
        
        print(f"Saved {content_type} to {filepath}")
        return filepath
    
    # Template definitions
    def _get_daily_newsletter_template(self) -> str:
        return """# {{title}}

*Generated: {{generated_at}}*

## Market Overview

- **Total Symbols Analyzed**: {{market_summary.total_symbols}}
- **Market Bias**: {{market_summary.market_bias}}
- **Average Confidence**: {{market_summary.average_confidence}}%
- **BUY Signals**: {{market_summary.buy_signals}}
- **SELL Signals**: {{market_summary.sell_signals}}
- **HOLD Signals**: {{market_summary.hold_signals}}

## Top BUY Signals ({{top_buy_signals|length}})

{{top_buy_signals}}

## Top SELL Signals ({{top_sell_signals|length}})

{{top_sell_signals}}

## Signal Summary

- **Total Signals**: {{signal_count.total}}
- **BUY**: {{signal_count.buy}} ({{signal_count.buy|divide:sigal_count.total|multiply:100|round:1}}%)
- **SELL**: {{signal_count.sell}} ({{signal_count.sell|divide:sigal_count.total|multiply:100|round:1}}%)
- **HOLD**: {{signal_count.hold}} ({{signal_count.hold|divide:sigal_count.total|multiply:100|round:1}}%)

---

*Note: This newsletter is generated automatically from the Volatile platform's technical analysis. 
All signals are for research purposes only and not financial advice.*
"""
    
    def _get_weekly_report_template(self) -> str:
        return """# {{title}}

*Week of {{week_start}} to {{week_end}}*
*Generated: {{generated_at}}*

## Executive Summary

This week's report analyzes {{market_summary.total_symbols}} symbols across stocks, crypto, and forex markets.

## Signal Performance

- **Total Signals Generated**: {{signal_performance.total_signals}}
- **BUY Signals**: {{signal_performance.buy_signals}}
- **SELL Signals**: {{signal_performance.sell_signals}}
- **Average BUY Confidence**: {{signal_performance.avg_buy_confidence}}%
- **Average SELL Confidence**: {{signal_performance.avg_sell_confidence}}%
- **High Confidence Signals** (>70%): {{signal_performance.high_confidence_signals}}

## Market Trends

{{market_trends}}

## Top Movers by Signal Strength

{{top_movers}}

## Looking Ahead

Based on current technical indicators and signal distribution, key areas to watch next week include:
- Continuation of current market bias
- Potential signal reversals in overextended positions
- Sector rotation patterns

---

*Report generated by Volatile Platform. Data as of {{generated_at}}. 
Not financial advice - for research purposes only.*
"""
    
    def _get_signal_alert_template(self) -> str:
        return """# 🚨 SIGNAL ALERT: {{symbol}}

*Generated: {{timestamp}}*
*Alert Level: {{alert_level}}*

## Signal Details

- **Symbol**: {{symbol}}
- **Signal**: {{signal}}
- **Strength**: {{strength}}%
- **Confidence**: {{confidence}}%
- **Reason**: {{reason}}

## Trading Considerations

Based on the {{alert_level}} alert level, consider the following:

{% if alert_level == "HIGH" %}
- **Strong signal detected** - This represents a high-conviction trading opportunity
- **Consider position sizing** appropriate to your risk tolerance
- **Monitor closely** for follow-through confirmation
{% elif alert_level == "MEDIUM" %}
- **Moderate signal** - Worth noting for watchlist or smaller position consideration
- **Look for confirmation** from price action or additional indicators
- **Use appropriate risk management**
{% else %}
- **Low signal strength** - Primarily for informational purposes
- **No immediate action suggested** based on this signal alone
{% endif %}

## Technical Context

This signal was generated by the Volatile platform's multi-indicator analysis engine,
combining RSI, MACD, Bollinger Bands, and Moving Average signals through weighted voting.

---

*Alert generated by Volatile Platform. 
Not financial advice - for research purposes only.*
"""
    
    def _get_market_summary_template(self) -> str:
        return """# {{title}}

*Generated: {{timestamp}}*

## Market Snapshot

- **Overall Bias**: {{overview.market_bias}}
- **Average Signal Confidence**: {{overview.average_confidence}}%
- **Market Breadth**: {{market_breadth}}% (percentage of bullish signals)

## Signal Distribution

- **BUY Signals**: {{signal_distribution.BUY}}
- **SELL Signals**: {{signal_distribution.SELECT}}  
- **HOLD Signals**: {{signal_distribution.HOLD}}

## High Confidence Signals (>70% Confidence)

{{high_confidence_signals}}

## Key Observations

1. Market showing {{overview.market_bias}} bias with {{overview.average_confidence}}% average confidence
2. {{high_confidence_signals|length}} high-confidence signals require attention
3. Signal distribution suggests {{overview.market_bias.lower()}} leaning market

---

*Summary generated by Volatile Platform. 
Not financial advice - for research purposes only.*
"""
    
    def _get_social_post_template(self) -> str:
        return """{{symbol}}: {{signal}} signal with {{confidence}}% confidence.

{{reason}}

#Volatile #Trading #Signals #{{symbol}}
"""

if __name__ == "__main__":
    # Demonstrate the content generation system
    print("Volatile Newsletter & Content Generation System")
    print("=" * 50)
    
    generator = ContentGenerator()
    
    # Generate daily newsletter
    print("\n1. Generating Daily Newsletter...")
    newsletter = generator.generate_daily_newsletter()
    print(f"   ✅ Saved to: {newsletter['filepath']}")
    print(f"   📄 Preview: {newsletter['content_preview'][:100]}...")
    
    # Generate market summary
    print("\n2. Generating Market Summary...")
    summary = generator.generate_market_summary()
    print(f"   ✅ Saved to: {summary['filepath']}")
    print(f"   📄 Preview: {summary['content_preview'][:100]}...")
    
    # Generate signal alerts for high confidence signals
    print("\n3. Checking for Signal Alerts...")
    signals = generator._get_all_signals()
    high_conf_signals = [s for s in signals if s.get('confidence', 0) > 70]
    
    if high_conf_signals:
        for signal in high_conf_signals[:2]:  # Limit to 2 alerts for demo
            alert = generator.generate_signal_alert(signal['symbol'], signal)
            print(f"   ✅ Alert for {signal['symbol']}: {alert['filepath']}")
    else:
        print("   ℹ️  No high-confidence signals (>70%) found for alerts")
    
    print("\n" + "=" * 50)
    print("Content Generation Demo Complete")