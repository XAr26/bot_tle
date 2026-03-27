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
                'defaultType': 'linear',
            },
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        # Check if proxy is set in environment (for Railway/US servers)
        proxy_url = os.getenv("PROXY_URL")
        if proxy_url:
            config['proxies'] = {
                'http': proxy_url,
                'https': proxy_url
            }
            logger.info(f"[BybitService] ✅ Proxy DETECTED: {proxy_url[:30]}...")
        else:
            logger.warning("[BybitService] ⚠️ No PROXY_URL found. Using alternative domain (api.bytick.com).")

        self.exchange = ccxt.bybit(config)
        
        # Override Bybit URL to bypass geo-blocking (CloudFront 403)
        # Must replace each key individually since urls['api'] is a dict, not a string
        if isinstance(self.exchange.urls.get('api'), dict):
            for key in self.exchange.urls['api']:
                if isinstance(self.exchange.urls['api'][key], str):
                    self.exchange.urls['api'][key] = self.exchange.urls['api'][key].replace(
                        'api.bybit.com', 'api.bytick.com'
                    )
        logger.info(f"[BybitService] api.bytick.com override applied ✅")
        
        self.exchange.set_sandbox_mode(False)
        self.markets_loaded = False



    async def fetch_ohlcv(self, symbol, timeframe='1m', limit=100):
        try:
            # Load markets once
            if not self.markets_loaded:
                logger.info(f"[BybitService] Loading markets for {symbol}...")
                await self.exchange.load_markets()
                self.markets_loaded = True
                logger.info("[BybitService] Bybit markets loaded ✅")

            # Symbol correction if needed
            if symbol not in self.exchange.markets:
                alt = symbol.replace("/", "")
                for m in self.exchange.markets:
                    if alt == m.replace("/", ""):
                        symbol = m
                        break

            logger.info(f"[BybitService] Fetching OHLCV: {symbol} {timeframe}")
            ohlcv = await self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )

            if not ohlcv:
                logger.warning(f"[BybitService] Empty data received for {symbol} ❌")
                return None

            logger.info(f"[BybitService] Got {len(ohlcv)} candles for {symbol} ✅")
            df = pd.DataFrame(ohlcv, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            return df

        except Exception as e:
            logger.error(f"[BybitService] ❌ Fetch error for {symbol}: {type(e).__name__}: {e}")
            return None

