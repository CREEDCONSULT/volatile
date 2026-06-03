# Volatile Market Data Ingestion Layer
# Phase 1: Core Research & Signal Engine - Week 1

import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataConnector:
    """Base class for market data connectors"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def get_price(self, symbol: str) -> Optional[Dict]:
        """Get current price for a symbol"""
        raise NotImplementedError
    
    def get_historical_data(self, symbol: str, period: str = '1d', interval: str = '1h') -> Optional[List[Dict]]:
        """Get historical data for a symbol"""
        raise NotImplementedError

class StockDataConnector(MarketDataConnector):
    """Connector for stock market data"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.example.com/stocks"  # Placeholder
    
    def get_price(self, symbol: str) -> Optional[Dict]:
        """Get current stock price"""
        try:
            # Placeholder implementation - would connect to real API
            logger.info(f"Fetching stock price for {symbol}")
            return {
                'symbol': symbol,
                'price': 100.0,  # Placeholder
                'timestamp': datetime.now().isoformat(),
                'source': 'placeholder'
            }
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = '1mo', interval: str = '1d') -> Optional[List[Dict]]:
        """Get historical stock data"""
        try:
            logger.info(f"Fetching historical data for {symbol}")
            # Placeholder data
            base_price = 100.0
            data = []
            for i in range(30):  # 30 days of data
                date = datetime.now() - timedelta(days=i)
                price = base_price + (i * 0.5)  # Simple trend
                data.append({
                    'timestamp': date.isoformat(),
                    'open': price - 1,
                    'high': price + 2,
                    'low': price - 2,
                    'close': price,
                    'volume': 1000000 + (i * 10000)
                })
            return list(reversed(data))  # Oldest first
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None

class CryptoDataConnector(MarketDataConnector):
    """Connector for cryptocurrency data"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.example.com/crypto"  # Placeholder
    
    def get_price(self, symbol: str) -> Optional[Dict]:
        """Get current crypto price"""
        try:
            logger.info(f"Fetching crypto price for {symbol}")
            return {
                'symbol': symbol,
                'price': 50000.0 if 'BTC' in symbol else 3000.0,  # Placeholder
                'timestamp': datetime.now().isoformat(),
                'source': 'placeholder'
            }
        except Exception as e:
            logger.error(f"Error fetching crypto price for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = '1mo', interval: str = '1h') -> Optional[List[Dict]]:
        """Get historical crypto data"""
        try:
            logger.info(f"Fetching historical crypto data for {symbol}")
            # Placeholder data
            base_price = 50000.0 if 'BTC' in symbol else 3000.0
            data = []
            for i in range(720):  # 30 days of hourly data
                timestamp = datetime.now() - timedelta(hours=i)
                price = base_price + (i * 0.1)  # Simple trend
                data.append({
                    'timestamp': timestamp.isoformat(),
                    'open': price - 10,
                    'high': price + 20,
                    'low': price - 20,
                    'close': price,
                    'volume': 100 + (i * 0.5)
                })
            return list(reversed(data))  # Oldest first
        except Exception as e:
            logger.error(f"Error fetching historical crypto data for {symbol}: {e}")
            return None

class ForexDataConnector(MarketDataConnector):
    """Connector for forex data"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.example.com/forex"  # Placeholder
    
    def get_price(self, symbol: str) -> Optional[Dict]:
        """Get current forex price"""
        try:
            logger.info(f"Fetching forex price for {symbol}")
            return {
                'symbol': symbol,
                'price': 1.2000 if 'EUR' in symbol else 1.0800,  # Placeholder
                'timestamp': datetime.now().isoformat(),
                'source': 'placeholder'
            }
        except Exception as e:
            logger.error(f"Error fetching forex price for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = '1mo', interval: str = '4h') -> Optional[List[Dict]]:
        """Get historical forex data"""
        try:
            logger.info(f"Fetching historical forex data for {symbol}")
            # Placeholder data
            base_price = 1.2000 if 'EUR' in symbol else 1.0800
            data = []
            for i in range(180):  # 30 days of 4-hour data
                timestamp = datetime.now() - timedelta(hours=i*4)
                price = base_price + (i * 0.0001)  # Simple trend
                data.append({
                    'timestamp': timestamp.isoformat(),
                    'open': price - 0.001,
                    'high': price + 0.002,
                    'low': price - 0.002,
                    'close': price,
                    'volume': 100000
                })
            return list(reversed(data))  # Oldest first
        except Exception as e:
            logger.error(f"Error fetching historical forex data for {symbol}: {e}")
            return None

class MarketDataAggregator:
    """Aggregates data from multiple sources"""
    
    def __init__(self):
        self.stocks = StockDataConnector()
        self.crypto = CryptoDataConnector()
        self.forex = ForexDataConnector()
        self.cache = {}
        self.cache_timeout = 30  # seconds
    
    def get_price(self, symbol: str, asset_type: str = 'auto') -> Optional[Dict]:
        """Get price for any symbol with automatic asset type detection"""
        # Check cache first
        cache_key = f"{symbol}_{asset_type}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return cached_data
        
        # Determine asset type if not specified
        if asset_type == 'auto':
            if any(crypto in symbol.upper() for crypto in ['BTC', 'ETH', 'USDT', 'BNB']):
                asset_type = 'crypto'
            elif len(symbol) == 6 and symbol.isalpha():  # Typical forex pair like EURUSD
                asset_type = 'forex'
            else:
                asset_type = 'stocks'
        
        # Fetch data based on type
        result = None
        if asset_type == 'stocks':
            result = self.stocks.get_price(symbol)
        elif asset_type == 'crypto':
            result = self.crypto.get_price(symbol)
        elif asset_type == 'forex':
            result = self.forex.get_price(symbol)
        
        # Cache result
        if result:
            self.cache[cache_key] = (result, time.time())
        
        return result
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Optional[Dict]]:
        """Get prices for multiple symbols"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_price(symbol)
        return results

def main():
    """Test the market data connectors"""
    print("Testing Volatile Market Data Ingestion Layer")
    print("=" * 50)
    
    aggregator = MarketDataAggregator()
    
    # Test stock data
    print("\n1. Testing Stock Data:")
    stock_price = aggregator.get_price('AAPL')
    print(f"AAPL: {stock_price}")
    
    # Test crypto data
    print("\n2. Testing Crypto Data:")
    crypto_price = aggregator.get_price('BTC')
    print(f"BTC: {crypto_price}")
    
    # Test forex data
    print("\n3. Testing Forex Data:")
    forex_price = aggregator.get_price('EURUSD')
    print(f"EURUSD: {forex_price}")
    
    # Test historical data
    print("\n4. Testing Historical Data:")
    hist_data = aggregator.stocks.get_historical_data('AAPL', period='1wk')
    if hist_data:
        print(f"AAPL Historical Data Points: {len(hist_data)}")
        print(f"Latest: {hist_data[-1] if hist_data else 'None'}")
    
    # Test multiple symbols
    print("\n5. Testing Multiple Symbols:")
    multi_prices = aggregator.get_multiple_prices(['AAPL', 'GOOGL', 'BTC', 'ETH', 'EURUSD'])
    for symbol, price in multi_prices.items():
        print(f"{symbol}: {price}")
    
    print("\n" + "=" * 50)
    print("Market Data Ingestion Layer Test Complete")

if __name__ == "__main__":
    main()