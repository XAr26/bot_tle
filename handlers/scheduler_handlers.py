from services.bybit_service import BybitService
from services.analysis_service import AnalysisService
from utils.formatter import Formatter
from utils.logger import setup_logger
from config.config import Config

logger = setup_logger()
bybit = BybitService()
analysis = AnalysisService()

async def send_auto_signals(context):
    """Callback function for auto signal updates."""
    # Assuming the bot info is stored in context.job.data or similar
    # In this case, we need at least one chat_id to send messages to
    # A real-world production bot might store chat IDs in a database.
    # For this demo, we'll log them but let's assume we need to broadcast.
    
    chat_id = context.job.data.get('chat_id')
    if not chat_id:
        logger.warning("No chat_id found for auto-signals.")
        return

    logger.info("Running auto-signal update...")

    for symbol in Config.DEFAULT_PAIRS:
        df = await bybit.fetch_ohlcv(symbol)
        if df is not None:
            df = analysis.calculate_indicators(df)
            signal = analysis.generate_signal(df)
            
            # Optionally, only send if signal is BUY or SELL
            if "BUY" in signal or "SELL" in signal:
                last_price = df.iloc[-1]['close']
                indicators = {
                    'rsi': df.iloc[-1]['rsi'],
                    'ma50': df.iloc[-1]['ma50'],
                    'ma200': df.iloc[-1]['ma200'],
                    'macd': df.iloc[-1]['macd']
                }
                report = Formatter.format_signal_message(symbol, last_price, signal, indicators)
                await context.bot.send_message(chat_id=chat_id, text=report, parse_mode='Markdown')
                logger.info(f"Auto-signal sent for {symbol} to chat {chat_id}")
