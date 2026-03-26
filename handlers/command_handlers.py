from telegram import Update
from telegram.ext import ContextTypes
from config.config import Config
from services.bybit_service import BybitService
from services.analysis_service import AnalysisService
from handlers.scheduler_handlers import send_auto_signals
from utils.formatter import Formatter
from utils.logger import setup_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from utils.chart import generate_chart

logger = setup_logger()
bybit = BybitService()
analysis = AnalysisService()


# ================= START =================
async def start_handler(update, context):
    keyboard = [
        [
            InlineKeyboardButton("📊 Signal", callback_data="signal"),
            InlineKeyboardButton("💰 Price", callback_data="price"),
        ],
        [
            InlineKeyboardButton("🔔 Auto ON", callback_data="auto_on"),
            InlineKeyboardButton("🔕 Auto OFF", callback_data="auto_off"),
        ],
        [
            InlineKeyboardButton("📖 Help", callback_data="help"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        "🚀 *Crypto Bot Menu*\n\nPilih menu di bawah:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "help":
        await help_handler(update, context)

    elif data == "signal":
        await query.edit_message_text("Gunakan: /signal BTC/USDT")

    elif data == "price":
        await query.edit_message_text("Gunakan: /price BTC/USDT")

    elif data == "auto_on":
        await auto_on_handler(update, context)

    elif data == "auto_off":
        await auto_off_handler(update, context)

# ================= HELP =================
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📖 *COMMAND LIST*

/start - Mulai bot
/help - Bantuan
/signal BTC/USDT - Analisa market
/price BTC/USDT - Harga realtime
/auto on - Aktifkan auto signal
/auto off - Matikan auto signal
"""
    await update.effective_message.reply_text(text, parse_mode='Markdown')


# ================= PRICE =================
async def price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Contoh: /price BTC/USDT")
        return

    symbol = context.args[0].upper()
    timeframe = '5m'
    
    # format symbol
    if "/" not in symbol:
        symbol_slash = symbol[:-4] + "/" + symbol[-4:]
        symbol_noslash = symbol
    else:
        symbol_slash = symbol
        symbol_noslash = symbol.replace("/", "")

    try:
        df = await bybit.fetch_ohlcv(symbol_slash, timeframe=timeframe)

        if df is None or df.empty:
            logger.info("Retrying without slash...")
            df = await bybit.fetch_ohlcv(symbol_noslash, timeframe=timeframe)

        price = df.iloc[-1]['close']

        await update.effective_message.reply_text(
            f"💰 Harga {symbol}: `{price}`",
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(e)
        await update.effective_message.reply_text("Error ambil harga")


# ================= AUTO ON =================
async def auto_on_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    job_name = f"auto_signal_{chat_id}"

    current_jobs = context.job_queue.get_jobs_by_name(job_name)

    if current_jobs:
        await update.effective_message.reply_text("⚠️ Auto signal sudah aktif")
        return

    context.job_queue.run_repeating(
        send_auto_signals,
        interval=Config.ANALYSIS_INTERVAL * 60,
        first=5,
        name=job_name,
        data={'chat_id': chat_id}
    )

    await update.effective_message.reply_text("✅ Auto signal AKTIF")


# ================= AUTO OFF =================
async def auto_off_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    job_name = f"auto_signal_{chat_id}"

    jobs = context.job_queue.get_jobs_by_name(job_name)

    if not jobs:
        await update.effective_message.reply_text("⚠️ Auto signal belum aktif")
        return

    for job in jobs:
        job.schedule_removal()

    await update.effective_message.reply_text("❌ Auto signal DIMATIKAN")

# ================= SIGNAL =================
async def signal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Contoh: /signal BTC/USDT")
        return

    raw_symbol = context.args[0].upper()

    # format symbol
    if "/" not in raw_symbol:
        symbol = raw_symbol[:-4] + "/" + raw_symbol[-4:]
    else:
        symbol = raw_symbol

    timeframe = context.args[1] if len(context.args) > 1 else '5m'

    await update.effective_message.reply_text(f"Analisa {symbol} ({timeframe})... ⏳")

    try:
        df = await bybit.fetch_ohlcv(symbol, timeframe=timeframe)

        if df is None or df.empty:
            await update.effective_message.reply_text("❌ Data kosong / pair tidak valid")
            return

        df = analysis.calculate_indicators(df)

        signal, confidence = analysis.generate_signal(df)
        price = df.iloc[-1]['close']

        indicators = {
            'rsi': df.iloc[-1].get('rsi'),
            'ma50': df.iloc[-1].get('ma50'),
            'ma200': df.iloc[-1].get('ma200'),
            'macd': df.iloc[-1].get('macd'),
        }

        report = Formatter.format_signal_message(
            symbol,
            price,
            signal,
            indicators,
            confidence
        )

        await update.effective_message.reply_text(report, parse_mode='Markdown')

    except Exception as e:
        logger.error(e)
        await update.effective_message.reply_text(f"❌ ERROR: {e}")