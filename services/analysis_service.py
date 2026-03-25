import pandas as pd
import ta
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from config.config import Config

class AnalysisService:
    @staticmethod
    def calculate_indicators(df):
        """Calculate technical indicators using the 'ta' library."""
        if df is None or df.empty:
            return None

        # RSI
        rsi = RSIIndicator(close=df['close'], window=Config.RSI_PERIOD)
        df['rsi'] = rsi.rsi()

        # Moving Averages
        ma50 = SMAIndicator(close=df['close'], window=Config.MA_FAST)
        ma200 = SMAIndicator(close=df['close'], window=Config.MA_SLOW)
        df['ma50'] = ma50.sma_indicator()
        df['ma200'] = ma200.sma_indicator()

        # MACD
        macd = MACD(
            close=df['close'],
            window_fast=Config.MACD_FAST,
            window_slow=Config.MACD_SLOW,
            window_sign=Config.MACD_SIGNAL
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()

        return df

    @staticmethod
    def generate_signal(df):
        """Generate trading signals based on indicators."""
        if df is None or df.empty:
            return "UNKNOWN"

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        rsi = last_row['rsi']
        ma50 = last_row['ma50']
        ma200 = last_row['ma200']
        macd_diff = last_row['macd_diff']
        prev_macd_diff = prev_row['macd_diff']

        # Logic for BUY
        # 1. RSI < 35 (Oversold) AND MACD Crossover (diff goes from <= 0 to > 0)
        # 2. Strong Buy: RSI < 25 AND MACD Crossover
        buy_signal = False
        strong_buy = False
        
        if rsi < 40 and macd_diff > 0 and prev_macd_diff <= 0:
            buy_signal = True
            if rsi < 25:
                strong_buy = True
        elif last_row['close'] > ma200 and rsi < 50 and macd_diff > 0 and prev_macd_diff <= 0:
            buy_signal = True

        # Logic for SELL
        # 1. RSI > 65 (Overbought) AND MACD Crossunder (diff goes from >= 0 to < 0)
        # 2. Strong Sell: RSI > 75 AND MACD Crossunder
        sell_signal = False
        strong_sell = False
        
        if rsi > 60 and macd_diff < 0 and prev_macd_diff >= 0:
            sell_signal = True
            if rsi > 75:
                strong_sell = True
        elif last_row['close'] < ma200 and rsi > 50 and macd_diff < 0 and prev_macd_diff >= 0:
            sell_signal = True

        if strong_buy:
            return "STRONG BUY 🚀🟢"
        elif buy_signal:
            return "BUY 🟢"
        elif strong_sell:
            return "STRONG SELL 💥🔴"
        elif sell_signal:
            return "SELL 🔴"
        else:
            return "WAIT 🟡"
