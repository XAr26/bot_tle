import ccxt
import os
from dotenv import load_dotenv

def test_bybit_sync():
    load_dotenv()
    
    exchange = ccxt.bybit({
        'enableRateLimit': True,
        'options': {'defaultType': 'linear'},
        'urls': {
            'api': {
                'public': 'https://api.bytick.com',
                'private': 'https://api.bytick.com',
            }
        }
    })
    
    try:
        print("Loading markets...")
        markets = exchange.load_markets()
        print(f"Loaded {len(markets)} markets.")
        
        # Look for BTC related symbols
        test_symbol = 'BTC/USDT'
        print(f"Testing find for: {test_symbol}")
        
        actual_symbol = None
        if test_symbol in exchange.markets:
            actual_symbol = test_symbol
        else:
            # Try matching logic
            alt = test_symbol.replace("/", "")
            for m in exchange.symbols:
                if alt == m.replace("/", "").split(":")[0]:
                    actual_symbol = m
                    break
        
        print(f"Resolved symbol: {actual_symbol}")
        
        if actual_symbol:
            ohlcv = exchange.fetch_ohlcv(actual_symbol, timeframe='1m', limit=5)
            print("Fetch successful!")
            print(ohlcv)
        else:
            print("Symbol not found in markets.")
            print("Sample symbols:", list(markets.keys())[:10])
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_bybit_sync()
