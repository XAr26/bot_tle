import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
    BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
    DEFAULT_PAIRS = os.getenv("DEFAULT_PAIRS", "BTC/USDT,ETH/USDT,BNB/USDT").split(",")
    ANALYSIS_INTERVAL = int(os.getenv("ANALYSIS_INTERVAL", 5))

    # Indicator parameters
    RSI_PERIOD = 14
    MA_FAST = 50
    MA_SLOW = 200
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
