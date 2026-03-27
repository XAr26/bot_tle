import aiohttp
import pandas as pd
from utils.logger import setup_logger
import os

logger = setup_logger()

# Use alternative domain to bypass CloudFront geo-blocking on Railway US servers
BYBIT_BASE_URL = os.getenv("BYBIT_BASE_URL", "https://api.bytick.com")

# Timeframe mapping: human-readable -> Bybit API interval string
TIMEFRAME_MAP = {
    '1m': '1', '3m': '3', '5m': '5', '15m': '15', '30m': '30',
    '1h': '60', '2h': '120', '4h': '240', '6h': '360', '12h': '720',
    '1d': 'D', '1w': 'W', '1M': 'M'
}

class BybitService:
    def __init__(self):
        self.base_url = BYBIT_BASE_URL
        proxy_url = os.getenv("PROXY_URL")
        self.proxy = proxy_url if proxy_url else None

        if self.proxy:
            logger.info(f"[BybitService] ✅ Proxy DETECTED: {self.proxy[:30]}...")
        logger.info(f"[BybitService] Using base URL: {self.base_url}")

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 100):
        """Fetch OHLCV candles directly from Bybit V5 API using aiohttp."""
        try:
            # Normalize symbol: 'BTC/USDT' -> 'BTCUSDT'
            category = 'linear'
            clean_symbol = symbol.replace("/", "").upper()

            interval = TIMEFRAME_MAP.get(timeframe, '5')

            url = f"{self.base_url}/v5/market/kline"
            params = {
                'category': category,
                'symbol': clean_symbol,
                'interval': interval,
                'limit': limit
            }

            logger.info(f"[BybitService] Fetching {clean_symbol} {timeframe} from {self.base_url}...")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, proxy=self.proxy, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    data = await resp.json()

            ret_code = data.get('retCode', -1)
            if ret_code != 0:
                logger.error(f"[BybitService] Bybit API error: {data.get('retMsg')} (code {ret_code})")
                return None

            raw_list = data.get('result', {}).get('list', [])
            if not raw_list:
                logger.warning(f"[BybitService] Empty candle data for {clean_symbol}")
                return None

            # Bybit returns newest-first, so we reverse to get oldest-first
            raw_list = list(reversed(raw_list))

            df = pd.DataFrame(raw_list, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
            ])
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype('int64'), unit='ms')
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

            logger.info(f"[BybitService] ✅ Got {len(df)} candles for {clean_symbol}")
            return df

        except Exception as e:
            logger.error(f"[BybitService] ❌ Fetch error for {symbol}: {type(e).__name__}: {e}")
            return None
