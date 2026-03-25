import ccxt.async_support as ccxt
import pandas as pd
from config.config import Config

class BinanceService:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': Config.BINANCE_API_KEY,
            'secret': Config.BINANCE_API_SECRET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        self.markets_loaded = False

    async def fetch_ohlcv(self, symbol, timeframe='5m', limit=250):
        try:
        # ===== LOAD MARKETS =====
            if not self.markets_loaded:
                await self.exchange.load_markets()
                self.markets_loaded = True
                print("MARKETS LOADED ✅")

            print("FETCH:", symbol)
            print("AVAILABLE:", symbol in self.exchange.markets)

        # 🔥 FIX UTAMA
            if symbol not in self.exchange.markets:
                print("❌ SYMBOL TIDAK ADA:", symbol)
                return None

            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

            if not ohlcv:
                print("❌ OHLCV EMPTY")
                return None

            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            print("DATA MASUK ✅", df.tail(1))

            return df

        except Exception as e:
            print(f"❌ ERROR FETCH {symbol}: {e}")
            return None