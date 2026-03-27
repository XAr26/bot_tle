import ccxt.async_support as ccxt
import pandas as pd
from utils.logger import setup_logger
import os

logger = setup_logger()

class BybitService:
    def __init__(self):
        config = {
            'enableRateLimit': True,
            'options': {
                'defaultType': 'linear'
            }
        }
        
        # Check if proxy is set in environment (for Railway/US servers)
        proxy_url = os.getenv("PROXY_URL")
        if proxy_url:
            config['proxies'] = {
                'http': proxy_url,
                'https': proxy_url
            }
            logger.info("Using Proxy for Bybit connection.")

        self.exchange = ccxt.bybit(config)
        # Set sandbox mode to False for production
        self.exchange.set_sandbox_mode(False)
        self.markets_loaded = False

    async def fetch_ohlcv(self, symbol, timeframe='1m', limit=100):
        try:
            # Load markets once
            if not self.markets_loaded:
                await self.exchange.load_markets()
                self.markets_loaded = True
                logger.info("Bybit markets loaded ✅")

            # Symbol correction if needed
            # Bybit usually uses 'BTC/USDT' or 'BTCUSDT' (spot)
            if symbol not in self.exchange.markets:
                alt = symbol.replace("/", "")
                for m in self.exchange.markets:
                    if alt == m.replace("/", ""):
                        symbol = m
                        break

            ohlcv = await self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )

            if not ohlcv:
                logger.warning(f"Empty data received for {symbol} on Bybit ❌")
                return None

            df = pd.DataFrame(ohlcv, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            return df

        except Exception as e:
            logger.error(f"Bybit fetch error for {symbol}: {e}")
            return None
