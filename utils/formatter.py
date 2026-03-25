class Formatter:
    @staticmethod
    def format_signal_message(symbol, price, signal, indicators):
        """Format the analysis signal into a nice Telegram message."""
        rsi = indicators.get('rsi', 0)
        ma50 = indicators.get('ma50', 0)
        ma200 = indicators.get('ma200', 0)
        macd = indicators.get('macd', 0)

        emoji_signal = "🟢 BUY" if "BUY" in signal else "🔴 SELL" if "SELL" in signal else "🟡 WAIT"

        message = (
            f"📊 *Trading Analysis: {symbol}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Price:* ${price:,.2f}\n"
            f"📢 *Signal:* {emoji_signal}\n\n"
            f"🔍 *Technical Indicators:*\n"
            f"• RSI: {rsi:.2f}\n"
            f"• MA50: ${ma50:,.2f}\n"
            f"• MA200: ${ma200:,.2f}\n"
            f"• MACD: {macd:.4f}\n\n"
            f"⏰ *Time:* Real-time data (5m interval)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *Disclaimer:* This is for informational purposes only. Trading involves risk."
        )
        return message

    @staticmethod
    def format_start_message():
        """Format help/start message."""
        return (
            "🚀 *Welcome to Professional Crypto Analysis Bot!* 🚀\n\n"
            "I provide real-time crypto trading signals based on technical analysis (RSI, MA, MACD).\n\n"
            "📌 *Supported Commands:*\n"
            "• /start - Show this information\n"
            "• /signal <pair> - Analyze a specific pair (e.g., /signal BTC/USDT)\n\n"
            "✅ *Features:*\n"
            "• Real-time Binance data\n"
            "• Multi-pair support\n"
            "• Auto signal updates every 5 minutes"
        )
