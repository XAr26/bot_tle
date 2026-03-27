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

    async def _get(self, endpoint: str, params: dict) -> dict | None:
        """Generic GET helper using aiohttp."""
        url = f"{self.base_url}{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params,
                    proxy=self.proxy,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"[BybitService] HTTP error ({endpoint}): {type(e).__name__}: {e}")
            return None

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 100):
        """Fetch OHLCV candles from Bybit V5 API."""
        try:
            clean_symbol = symbol.replace("/", "").upper()
            interval = TIMEFRAME_MAP.get(timeframe, '5')

            logger.info(f"[BybitService] Fetching OHLCV {clean_symbol} {timeframe}...")
            data = await self._get('/v5/market/kline', {
                'category': 'linear',
                'symbol': clean_symbol,
                'interval': interval,
                'limit': limit
            })

            if not data or data.get('retCode', -1) != 0:
                logger.error(f"[BybitService] API error: {data.get('retMsg') if data else 'No response'}")
                return None

            raw_list = data.get('result', {}).get('list', [])
            if not raw_list:
                logger.warning(f"[BybitService] Empty candle data for {clean_symbol}")
                return None

            # Bybit returns newest-first, reverse to oldest-first
            raw_list = list(reversed(raw_list))

            df = pd.DataFrame(raw_list, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
            ])
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype('int64'), unit='ms')
            df[['open', 'high', 'low', 'close', 'volume']] = (
                df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            )

            logger.info(f"[BybitService] ✅ Got {len(df)} candles for {clean_symbol}")
            return df

        except Exception as e:
            logger.error(f"[BybitService] ❌ fetch_ohlcv error for {symbol}: {type(e).__name__}: {e}")
            return None

    async def fetch_ticker(self, symbol: str) -> dict | None:
        """Fetch 24h ticker data (price, change%, volume) for a symbol."""
        try:
            clean_symbol = symbol.replace("/", "").upper()
            data = await self._get('/v5/market/tickers', {
                'category': 'linear',
                'symbol': clean_symbol
            })

            if not data or data.get('retCode', -1) != 0:
                return None

            tickers = data.get('result', {}).get('list', [])
            if not tickers:
                return None

            t = tickers[0]
            return {
                'symbol': clean_symbol,
                'price': float(t.get('lastPrice', 0)),
                'change_24h': float(t.get('price24hPcnt', 0)) * 100,
                'high_24h': float(t.get('highPrice24h', 0)),
                'low_24h': float(t.get('lowPrice24h', 0)),
                'volume_24h': float(t.get('volume24h', 0)),
            }

        except Exception as e:
            logger.error(f"[BybitService] ❌ fetch_ticker error for {symbol}: {type(e).__name__}: {e}")
            return None

    async def fetch_top_movers(self, limit: int = 10) -> list | None:
        """Fetch top gainers and losers from linear (USDT perpetual) market."""
        try:
            data = await self._get('/v5/market/tickers', {'category': 'linear'})

            if not data or data.get('retCode', -1) != 0:
                return None

            tickers = data.get('result', {}).get('list', [])
            if not tickers:
                return None

            # Only include USDT pairs with meaningful volume
            filtered = []
            for t in tickers:
                sym = t.get('symbol', '')
                if not sym.endswith('USDT'):
                    continue
                try:
                    change = float(t.get('price24hPcnt', 0)) * 100
                    vol = float(t.get('volume24h', 0))
                    price = float(t.get('lastPrice', 0))
                    if vol > 1_000_000 and price > 0:  # filter low-volume coins
                        filtered.append({
                            'symbol': sym,
                            'price': price,
                            'change_24h': change,
                            'volume_24h': vol,
                        })
                except Exception:
                    continue

            # Sort by change descending
            filtered.sort(key=lambda x: x['change_24h'], reverse=True)
            return filtered

        except Exception as e:
            logger.error(f"[BybitService] ❌ fetch_top_movers error: {type(e).__name__}: {e}")
            return None
