#!/usr/bin/env python3
"""
Volatile Market Data Ingestion - Real Implementation
Fetches real market data and stores as markdown notes in the Obsidian vault.
"""

import yfinance as yf
import pycoingecko
import requests
import json
from datetime import datetime
import os

# Configuration
VAULT_RESEARCH_PATH = "/mnt/c/CreedAI/obsidian-vault/03_Volatile/Research/market_data/"
SYMBOLS = {
    'stocks': ['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
    'crypto': ['bitcoin', 'ethereum', 'binancecoin'],
    'forex': ['EUR/USD', 'GBP/USD', 'USD/JPY']  # Note: Frankfurter uses different format
}

# Ensure directory exists
os.makedirs(VAULT_RESEARCH_PATH, exist_ok=True)

def fetch_stock_data(symbol):
    """Fetch stock data using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        # Get historical data for the last 7 days
        hist = ticker.history(period="7d")
        if hist.empty:
            return None
        # Convert to list of dicts for easier handling
        data = []
        for date, row in hist.iterrows():
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Open': round(row['Open'], 2),
                'High': round(row['High'], 2),
                'Low': round(row['Low'], 2),
                'Close': round(row['Close'], 2),
                'Volume': int(row['Volume'])
            })
        return {
            'symbol': symbol,
            'data': data,
            'last_updated': datetime.now().isoformat(),
            'source': 'yfinance'
        }
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return None

def fetch_crypto_data(symbol_id):
    """Fetch crypto data using CoinGecko."""
    try:
        cg = pycoingecko.CoinGeckoAPI()
        # Get market data for the last 7 days
        market_data = cg.get_coin_market_chart_by_id(id=symbol_id, vs_currency='usd', days=7)
        if not market_data or 'prices' not in market_data:
            return None
        prices = market_data['prices']  # List of [timestamp, price]
        # Convert to daily OHLC? We'll simplify to daily close price for now
        # Group by date
        from collections import defaultdict
        daily_data = defaultdict(list)
        for timestamp, price in prices:
            dt = datetime.fromtimestamp(timestamp/1000)
            date_str = dt.strftime('%Y-%m-%d')
            daily_data[date_str].append(price)
        
        # Create OHLCV-like data (we don't have volume from this endpoint, so we'll set volume to 0)
        data = []
        for date_str, price_list in sorted(daily_data.items()):
            open_price = min(price_list)  # Approximation
            high_price = max(price_list)
            low_price = min(price_list)
            close_price = price_list[-1]  # Last price of the day
            data.append({
                'Date': date_str,
                'Open': round(open_price, 2),
                'High': round(high_price, 2),
                'Low': round(low_price, 2),
                'Close': round(close_price, 2),
                'Volume': 0  # Placeholder
            })
        return {
            'symbol': symbol_id,
            'data': data,
            'last_updated': datetime.now().isoformat(),
            'source': 'coingecko'
        }
    except Exception as e:
        print(f"Error fetching crypto data for {symbol_id}: {e}")
        return None

def fetch_forex_data(pair):
    """Fetch forex data using Frankfurter API."""
    try:
        # Frankfurter API format: https://api.frankfurter.dev/v1/
        # For a pair like EUR/USD, we need to separate base and target
        base, target = pair.split('/')
        # Get data for the last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        url = f"https://api.frankfurter.dev/v1/{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
        params = {
            'from': base,
            'to': target
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Forex API error for {pair}: {response.status_code}")
            return None
        data = response.json()
        if 'rates' not in data:
            return None
        # Convert rates to our format
        # data['rates'] is a dict: {date: {target: rate}}
        rates = data['rates']
        formatted_data = []
        for date_str, rates_dict in sorted(rates.items()):
            rate = rates_dict.get(target)
            if rate is None:
                continue
            # For forex, we don't have OHLC from this API, so we'll use the same rate for all
            # In a real system, we'd use an API that provides OHLC
            formatted_data.append({
                'Date': date_str,
                'Open': round(rate, 4),
                'High': round(rate, 4),
                'Low': round(rate, 4),
                'Close': round(rate, 4),
                'Volume': 0  # Placeholder
            })
        return {
            'symbol': pair,
            'data': formatted_data,
            'last_updated': datetime.now().isoformat(),
            'source': 'frankfurter'
        }
    except Exception as e:
        print(f"Error fetching forex data for {pair}: {e}")
        return None

def save_as_markdown_note(symbol_data):
    """Save symbol data as a markdown note in the vault."""
    if not symbol_data or not symbol_data.get('data'):
        return False
    
    symbol = symbol_data['symbol']
    # Create a safe filename
    safe_filename = symbol.replace('/', '-').replace(' ', '_') + '.md'
    filepath = os.path.join(VAULT_RESEARCH_PATH, safe_filename)
    
    # Build markdown content
    md_content = f"""---
symbol: {symbol}
source: {symbol_data['source']}
last_updated: {symbol_data['last_updated']}
data_points: {len(symbol_data['data'])}
---

# Market Data for {symbol}

*Last updated: {symbol_data['last_updated']}*
*Source: {symbol_data['source']}*

| Date | Open | High | Low | Close | Volume |
|------|------|------|-----|-------|--------|
"""
    for day in symbol_data['data']:
        md_content += f"| {day['Date']} | {day['Open']} | {day['High']} | {day['Low']} | {day['Close']} | {day['Volume']} |\n"
    
    md_content += f"\n*Note: This data is for research purposes only and not financial advice.*\n"
    
    # Write to file
    try:
        with open(filepath, 'w') as f:
            f.write(md_content)
        print(f"Saved note for {symbol} to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving note for {symbol}: {e}")
        return False

def main():
    """Main function to fetch and store market data."""
    print("Starting Volatile Market Data Ingestion...")
    print(f"Vault path: {VAULT_RESEARCH_PATH}")
    
    total_saved = 0
    
    # Process stocks
    print("\n=== Fetching Stock Data ===")
    for symbol in SYMBOLS['stocks']:
        print(f"Fetching {symbol}...")
        data = fetch_stock_data(symbol)
        if data and save_as_markdown_note(data):
            total_saved += 1
    
    # Process crypto
    print("\n=== Fetching Crypto Data ===")
    for symbol_id in SYMBOLS['crypto']:
        print(f"Fetching {symbol_id}...")
        data = fetch_crypto_data(symbol_id)
        if data and save_as_markdown_note(data):
            total_saved += 1
    
    # Process forex
    print("\n=== Fetching Forex Data ===")
    for pair in SYMBOLS['forex']:
        print(f"Fetching {pair}...")
        data = fetch_forex_data(pair)
        if data and save_as_markdown_note(data):
            total_saved += 1
    
    print(f"\n=== Completed ===")
    print(f"Successfully saved {total_saved} market data notes.")
    
    # List the created files
    print("\nCreated files:")
    for file in os.listdir(VAULT_RESEARCH_PATH):
        if file.endswith('.md'):
            print(f"  - {file}")

if __name__ == "__main__":
    from datetime import timedelta  # Import here to avoid issues if not used
    main()