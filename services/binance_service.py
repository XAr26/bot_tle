import ccxt.async_support as ccxt
import pandas as pd
from config.config import Config

class BinanceService:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': Config.BINANCE_API_KEY,
            'secret': Config.BINANCE_API_SECRET,
            'enableRateLimit': True,
        })

    async def fetch_ohlcv(self, symbol, timeframe='5m', limit=250):
        """Fetch OHLCV data for a specific symbol using async support."""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    async def close(self):
        """Close the exchange connection."""
        await self.exchange.close()

    def get_supported_pairs(self):
        """Returns a list of supported pairs from config or exchange."""
        return Config.DEFAULT_PAIRS
