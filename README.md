# Volatile Trading Platform

An agent-driven trading research platform for stocks, crypto, and forex with automated signal generation, research workflows, and content creation.

## 📋 Overview

Volatile is a trading platform that provides:
- **Agent-driven research**: Automated market research workflows
- **Technical analysis**: Real-time signal generation using multiple indicators
- **Data integration**: Stocks, crypto, and forex market data
- **Knowledge persistence**: All research stored in Obsidian vault as source of truth
- **Automated workflows**: From data ingestion to signal generation to content creation

## 🏗️ Architecture

```
Market Data Layer → Technical Indicators → Signal Generation → Content/Newsletter → Community Features
       ↓                    ↓                   ↓                  ↓                   ↓
Yahoo Finance     RSI, MACD, Bollinger    Weighted Voting    Newsletter Templates   User Profiles
CoinGecko         Bands, Moving Averages  (BUY/SELL/HOLD)    Automated Publishing   Reputation System
Frankfurter API                                        Email/Telegram/Web     Discussion Forums
```

## 🔧 Current Implementation (Phase 1 Complete)

### ✅ Market Data Ingestion Layer
- **Stocks**: Yahoo Finance integration (AAPL, GOOGL, MSFT, TSLA)
- **Crypto**: CoinGecko integration (BTC, ETH, BNB)
- **Forex**: Frankfurter API integration (EUR/USD, GBP/USD, USD/JPY)
- **Data storage**: OHLCV data saved as markdown notes in vault
- **Features**: Caching, error handling, rate limiting

### ✅ Technical Indicator Library
- **RSI** (Relative Strength Index): 14-period
- **MACD**: (12,26,9) default settings
- **Bollinger Bands**: (20,2) standard deviation
- **Moving Averages**: SMA(20), SMA(50), SMA(200)
- **Storage**: Indicator values saved with market data

### ✅ Signal Generation Engine
- **Multi-indicator signals**: RSI, MACD, Bollinger Bands, Moving Averages
- **Weighted voting**: Combines signals based on indicator strength
- **Output**: BUY/SELL/HOLD with strength (0-100%) and confidence (0-100%)
- **Storage**: Trading signals saved as markdown notes in vault

## 📁 Vault Structure

All data is stored in the Obsidian vault as the source of truth:

```
/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/
├── market_data/          # Raw OHLCV data (10 symbols)
│   ├── AAPL.md
│   ├── GOOGL.md
│   └── ... (forex/crypto pairs)
├── indicators/           # Technical indicators (10 symbols)
│   ├── AAPL_indicators.md
│   ├── bitcoin_indicators.md
│   └── ...
└── signals/              # Trading signals (10 symbols)
    ├── AAPL_signal.md
    ├── ethereum_signal.md
    └── ...
```

## 🧪 Validation & Quality Assurance

Each component includes automated validation checkpoints:

1. **Market Data Checkpoint**: Validates data retrieval and storage
2. **Indicator Checkpoint**: Confirms technical calculations
3. **Signal Checkpoint**: Verifies signal generation and storage

All validations are currently passing.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Required packages: `yfinance`, `pycoingecko`, `requests`, `pandas`, `numpy`

### Installation
```bash
pip install yfinance pycoingecko requests pandas numpy
```

### Usage
```bash
# Fetch market data
python fetch_market_data.py

# Calculate technical indicators
python batch_indicators.py

# Generate trading signals
python batch_signals.py

# Run validation checkpoints
python validate_checkpoint1.py  # Market data
python validate_checkpoint2.py  # Indicators
python validate_checkpoint3.py  # Signals
```

## 📊 Sample Output

Each vault note includes:
- YAML frontmatter with metadata
- Data tables with OHLCV values
- Research disclaimers
- Timestamps and source attribution

Example signal note frontmatter:
```yaml
---
symbol: AAPL
signal: HOLD
strength: 45.2
confidence: 78.5
timestamp: 2026-06-03T18:00:00Z
---
```

## 📈 Future Roadmap

### Phase 2: Newsletter & Content System (Weeks 4-6)
- Automated content generation from signals and research
- Multi-format output (email, Telegram, web, vault)
- Template system for different content types
- Engagement tracking and A/B testing

### Phase 3: Community Intelligence (Weeks 7-9)
- User profiles and watchlists
- Collaborative filtering and reputation system
- Social trading elements and idea sharing
- Community-driven signal validation

## 🔒 Disclaimers

⚠️ **Important**: All signals and research outputs are for informational and educational purposes only. They do not constitute financial advice, investment recommendations, or trading signals. Users should conduct their own research and consult with qualified financial advisors before making any investment decisions.

The Volatile platform treats all notes as financial research context, not as directives for trading actions.

## 📄 License

This project is proprietary to Creed Consult and part of the CreedAI ecosystem.

## 🙏 Acknowledgments

Built using:
- Yahoo Finance (via yfinance)
- CoinGecko API
- Frankfurter API
- Obsidian vault as knowledge base
- CreedAI infrastructure patterns

---

*Last updated: June 3, 2026*
*Version: 0.1.0 (Phase 1 Complete)*