import asyncio
import ccxt.async_support as ccxt
import os
import certifi
import ssl

async def test_proxy():
    proxy_url = "http://npetlpis:n4tj72g8o4sz@31.59.20.176:6754"
    print(f"Testing proxy: {proxy_url}")
    
    # Configure exchange
    exchange = ccxt.bybit({
        'enableRateLimit': True,
        'options': {'defaultType': 'linear'},
        'proxies': {
            'http': proxy_url,
            'https': proxy_url
        }
    })
    
    try:
        print("Loading markets...")
        await exchange.load_markets()
        print("Markets loaded successfully!")
        
        print("Fetching OHLCV for BTC/USDT...")
        ohlcv = await exchange.fetch_ohlcv('BTC/USDT', timeframe='1m', limit=5)
        if ohlcv:
            print(f"Success! Data length: {len(ohlcv)}")
        else:
            print("Received empty data.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(test_proxy())
