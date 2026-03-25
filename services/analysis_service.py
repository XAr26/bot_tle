import pandas as pd
import ta
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from config.config import Config


class AnalysisService:

    @staticmethod
    def calculate_indicators(df):
        """Calculate technical indicators using TA library"""

        if df is None or df.empty:
            return None

        # ===== RSI =====
        rsi = RSIIndicator(close=df['close'], window=Config.RSI_PERIOD)
        df['rsi'] = rsi.rsi()

        # ===== MOVING AVERAGE =====
        ma50 = SMAIndicator(close=df['close'], window=Config.MA_FAST)
        ma200 = SMAIndicator(close=df['close'], window=Config.MA_SLOW)

        df['ma50'] = ma50.sma_indicator()
        df['ma200'] = ma200.sma_indicator()

        # ===== MACD =====
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
        """AI-based signal using scoring system"""

        if df is None or df.empty:
            return "UNKNOWN", 0

        # Pastikan cukup data
        if len(df) < 2:
            return "WAIT 🟡", 0

        last = df.iloc[-1]
        prev = df.iloc[-2]

        score = 0

        # ===== RSI =====
        if last['rsi'] < 30:
            score += 2
        elif last['rsi'] < 40:
            score += 1
        elif last['rsi'] > 70:
            score -= 2
        elif last['rsi'] > 60:
            score -= 1

        # ===== MACD CROSS =====
        if last['macd_diff'] > 0 and prev['macd_diff'] <= 0:
            score += 2
        elif last['macd_diff'] < 0 and prev['macd_diff'] >= 0:
            score -= 2

        # ===== TREND MA =====
        if last['ma50'] > last['ma200']:
            score += 1
        else:
            score -= 1

        # ===== PRICE POSITION =====
        if last['close'] > last['ma50']:
            score += 1
        else:
            score -= 1

        # ===== VOLUME BOOST =====
        if 'volume' in df.columns:
            if last['volume'] > df['volume'].mean():
                score += 1

        # ===== DECISION =====
        if score >= 5:
            signal = "STRONG BUY 🚀🟢"
        elif score >= 3:
            signal = "BUY 🟢"
        elif score <= -5:
            signal = "STRONG SELL 💥🔴"
        elif score <= -3:
            signal = "SELL 🔴"
        else:
            signal = "WAIT 🟡"

        # ===== CONFIDENCE =====
        confidence = min(abs(score) / 6 * 100, 100)

        return signal, confidence