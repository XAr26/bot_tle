import ccxt.async_support as ccxt
import pandas as pd

class BinanceService:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'timeout': 30000,
            'options': {
                'defaultType': 'spot'
            }
        })

        # ✅ HARUS DI SINI
        self.exchange.set_sandbox_mode(False)

        self.markets_loaded = False

    async def fetch_ohlcv(self, symbol, timeframe='5m', limit=100):
        try:
            # load market sekali
            if not self.markets_loaded:
                await self.exchange.load_markets()
                self.markets_loaded = True
                print("MARKETS LOADED ✅")

            print("=== DEBUG BINANCE ===")
            print("INPUT:", symbol)

            print("MARKETS COUNT:", len(self.exchange.markets))

            # AUTO FIX SYMBOL
            if symbol not in self.exchange.markets:
                alt = symbol.replace("/", "")
                for m in self.exchange.markets:
                    if alt == m.replace("/", ""):
                        print("FIXED SYMBOL:", m)
                        symbol = m
                        break

            print("FINAL SYMBOL:", symbol)

            ohlcv = await self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )

            if not ohlcv:
                print("EMPTY DATA ❌")
                return None

            df = pd.DataFrame(ohlcv, columns=[
                'timestamp','open','high','low','close','volume'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            print("DATA OK ✅", len(df))
            return df

        except Exception as e:
            print("FETCH ERROR:", e)
            return None