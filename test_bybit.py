import asyncio
import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

async def test_bybit():
    load_dotenv()
    
    exchange = ccxt.bybit({
        'enableRateLimit': True,
        'options': {'defaultType': 'linear'},
    })
    
    try:
        print("Loading markets...")
        markets = await exchange.load_markets()
        print(f"Loaded {len(markets)} markets.")
        
        # Look for BTC related symbols
        btc_symbols = [s for s in exchange.symbols if 'BTC' in s]
        print(f"Sample BTC symbols: {btc_symbols[:10]}")
        
        test_symbol = 'BTC/USDT'
        print(f"Testing fetch_ohlcv for: {test_symbol}")
        
        # Try to find the actual symbol name in CCXT
        actual_symbol = None
        if test_symbol in exchange.markets:
            actual_symbol = test_symbol
        else:
            alt = test_symbol.replace("/", "")
            for m in exchange.symbols:
                if alt in m.replace("/", "").replace(":", ""):
                    actual_symbol = m
                    break
        
        print(f"Resolved symbol: {actual_symbol}")
        
        if actual_symbol:
            ohlcv = await exchange.fetch_ohlcv(actual_symbol, timeframe='1m', limit=5)
            print("Fetch successful!")
            print(ohlcv)
        else:
            print("Symbol not found in markets.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(test_bybit())
