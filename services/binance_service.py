import ccxt.async_support as ccxt
import pandas as pd
from config.config import Config

class BinanceService:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        self.markets_loaded = False

    async def fetch_ohlcv(self, symbol, timeframe='5m', limit=250):
    try:
        if not self.markets_loaded:
            await self.exchange.load_markets()
            self.markets_loaded = True
            print("MARKETS LOADED ✅")

        print("INPUT SYMBOL:", symbol)

        # AUTO FIX SYMBOL
        if symbol not in self.exchange.markets:
            alt = symbol.replace("/", "")
            for market in self.exchange.markets:
                if alt == market.replace("/", ""):
                    print("FIXED SYMBOL:", market)
                    symbol = market
                    break

        print("FINAL SYMBOL:", symbol)

        ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

        if not ohlcv:
            print("OHLCV EMPTY ❌")
            return None

        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        print("DATA OK ✅", len(df))

        return df

    except Exception as e:
        print("ERROR FETCH:", e)
        return None