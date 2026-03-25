class Formatter:

    @staticmethod
    def format_signal_message(symbol, price, signal, indicators, confidence, timeframe="5m"):
        """Format AI signal into a professional Telegram message."""

        rsi = indicators.get('rsi', 0) or 0
        ma50 = indicators.get('ma50', 0) or 0
        ma200 = indicators.get('ma200', 0) or 0
        macd = indicators.get('macd', 0) or 0

        # ===== EMOJI SIGNAL =====
        if "STRONG BUY" in signal:
            emoji_signal = "🚀 STRONG BUY"
        elif "BUY" in signal:
            emoji_signal = "🟢 BUY"
        elif "STRONG SELL" in signal:
            emoji_signal = "💥 STRONG SELL"
        elif "SELL" in signal:
            emoji_signal = "🔴 SELL"
        else:
            emoji_signal = "🟡 WAIT"

        # ===== TREND DETECTION =====
        trend = "📈 UP TREND" if ma50 > ma200 else "📉 DOWN TREND"

        # ===== CONFIDENCE SAFE =====
        confidence = max(0, min(confidence, 100))

        # ===== CONFIDENCE BAR =====
        bars = int(confidence // 10)
        confidence_bar = "█" * bars + "░" * (10 - bars)

        message = (
            f"📊 *AI TRADING SIGNAL*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💱 *Pair:* `{symbol}`\n"
            f"💰 *Price:* `${price:,.2f}`\n\n"

            f"📢 *Signal:* *{emoji_signal}*\n"
            f"{trend}\n\n"

            f"📈 *Confidence:* `{confidence:.0f}%`\n"
            f"`{confidence_bar}`\n\n"

            f"🔍 *Indicators:*\n"
            f"• RSI: `{rsi:.2f}`\n"
            f"• MA50: `{ma50:,.2f}`\n"
            f"• MA200: `{ma200:,.2f}`\n"
            f"• MACD: `{macd:.4f}`\n\n"

            f"⏱ *Timeframe:* `{timeframe}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _Not financial advice. Trade at your own risk._"
        )

        return message

    @staticmethod
    def format_start_message():
        return (
            "🚀 *AI Crypto Trading Bot* 🚀\n\n"
            "Bot ini menggunakan analisa AI (RSI, MA, MACD + scoring system).\n\n"
            "📌 *Commands:*\n"
            "• /start - Menu utama\n"
            "• /signal BTC/USDT - Analisa pair\n"
            "• /price BTC/USDT - Harga realtime\n"
            "• /auto_on - Auto signal ON\n"
            "• /auto_off - Auto signal OFF\n\n"
            "🔥 *Features:*\n"
            "• AI Signal + Confidence\n"
            "• Multi indikator\n"
            "• Chart otomatis\n"
            "• Real-time data\n\n"
            "⚡ _Powered by AI Trading Engine_"
        )