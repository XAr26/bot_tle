from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config.config import Config
from services.bybit_service import BybitService
from services.analysis_service import AnalysisService
from handlers.scheduler_handlers import send_auto_signals
from utils.formatter import Formatter
from utils.logger import setup_logger

logger = setup_logger()
bybit = BybitService()
analysis = AnalysisService()

# Daftar pair populer untuk fitur /market
POPULAR_PAIRS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
    'DOGEUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOTUSDT', 'MATICUSDT',
    'LINKUSDT', 'LTCUSDT', 'TRXUSDT', 'NEARUSDT', 'ATOMUSDT',
]

def normalize_symbol(raw: str) -> str:
    """Normalize symbol input. Accepts: BTC, BTCUSDT, BTC/USDT -> BTCUSDT"""
    raw = raw.upper().strip().replace("/", "").replace("-", "")
    if not raw.endswith("USDT") and not raw.endswith("BTC") and not raw.endswith("ETH"):
        raw = raw + "USDT"
    return raw


# ================= START =================
async def start_handler(update, context):
    keyboard = [
        [
            InlineKeyboardButton("📊 Signal", callback_data="signal"),
            InlineKeyboardButton("💰 Harga", callback_data="price"),
        ],
        [
            InlineKeyboardButton("🌍 Market", callback_data="market"),
            InlineKeyboardButton("🚀 Top Gainers", callback_data="top"),
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
        "🤖 *Crypto Analysis Bot*\n\nPilih menu di bawah atau ketik nama coin (contoh: `btc`, `eth`, `sol`):",
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
        await query.edit_message_text("Gunakan: `/signal BTC/USDT` atau ketik `btc`", parse_mode="Markdown")
    elif data == "price":
        await query.edit_message_text("Gunakan: `/price BTC/USDT` atau ketik `btc`", parse_mode="Markdown")
    elif data == "market":
        await market_handler(update, context)
    elif data == "top":
        await top_handler(update, context)
    elif data == "auto_on":
        await auto_on_handler(update, context)
    elif data == "auto_off":
        await auto_off_handler(update, context)


# ================= HELP =================
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📖 *COMMAND LIST*

/start — Menu utama
/help — Bantuan ini
/signal BTC — Analisa teknikal + sinyal
/price BTC — Harga & statistik 24h
/market — Overview harga banyak coin
/top — Top gainers & losers hari ini
/auto\_on — Aktifkan auto signal
/auto\_off — Matikan auto signal

💡 *Shortcut:* Cukup ketik nama coin:
`btc`, `eth`, `sol`, `xrp`, `doge`, dll.
"""
    await update.effective_message.reply_text(text, parse_mode='Markdown')


# ================= PRICE =================
async def price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Contoh: /price BTC atau /price BTC/USDT")
        return

    symbol = normalize_symbol(context.args[0])
    ticker = await bybit.fetch_ticker(symbol)

    if not ticker:
        await update.effective_message.reply_text(f"❌ Pair `{symbol}` tidak ditemukan.", parse_mode='Markdown')
        return

    change = ticker['change_24h']
    arrow = "🟢" if change >= 0 else "🔴"
    sign = "+" if change >= 0 else ""

    text = (
        f"💰 *{ticker['symbol']}*\n\n"
        f"Harga: `${ticker['price']:,.4f}`\n"
        f"24h: {arrow} `{sign}{change:.2f}%`\n"
        f"High 24h: `${ticker['high_24h']:,.4f}`\n"
        f"Low 24h: `${ticker['low_24h']:,.4f}`\n"
        f"Volume 24h: `{ticker['volume_24h']:,.0f}`"
    )
    await update.effective_message.reply_text(text, parse_mode='Markdown')


# ================= MARKET OVERVIEW =================
async def market_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("⏳ Mengambil data market...")

    lines = ["🌍 *Market Overview*\n"]
    failed = 0
    for pair in POPULAR_PAIRS:
        ticker = await bybit.fetch_ticker(pair)
        if not ticker:
            failed += 1
            continue
        change = ticker['change_24h']
        arrow = "🟢" if change >= 0 else "🔴"
        name = pair.replace("USDT", "")
        lines.append(f"{arrow} *{name}*: `${ticker['price']:,.4f}` ({'+' if change>=0 else ''}{change:.2f}%)")

    if len(lines) == 1:
        await update.effective_message.reply_text("❌ Gagal mengambil data market.")
        return

    lines.append(f"\n_Data dari Bybit · {len(lines)-1} pairs_")
    await update.effective_message.reply_text("\n".join(lines), parse_mode='Markdown')


# ================= TOP GAINERS / LOSERS =================
async def top_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("⏳ Mengambil data top mover...")

    movers = await bybit.fetch_top_movers()
    if not movers:
        await update.effective_message.reply_text("❌ Gagal mengambil data top movers.")
        return

    gainers = movers[:5]
    losers = movers[-5:][::-1]

    lines = ["🚀 *Top Gainers & Losers 24H*\n"]
    lines.append("*📈 Top Gainers:*")
    for i, c in enumerate(gainers, 1):
        name = c['symbol'].replace('USDT', '')
        lines.append(f"{i}. *{name}*: `+{c['change_24h']:.2f}%` @ `${c['price']:,.4f}`")

    lines.append("\n*📉 Top Losers:*")
    for i, c in enumerate(losers, 1):
        name = c['symbol'].replace('USDT', '')
        lines.append(f"{i}. *{name}*: `{c['change_24h']:.2f}%` @ `${c['price']:,.4f}`")

    lines.append("\n_Data dari Bybit Futures (USDT Perp)_")
    await update.effective_message.reply_text("\n".join(lines), parse_mode='Markdown')


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
        await update.effective_message.reply_text("Contoh: /signal BTC atau /signal ETH 1h")
        return

    symbol = normalize_symbol(context.args[0])
    timeframe = context.args[1] if len(context.args) > 1 else '5m'

    await update.effective_message.reply_text(f"⏳ Analisa *{symbol}* ({timeframe})...", parse_mode='Markdown')

    try:
        df = await bybit.fetch_ohlcv(symbol, timeframe=timeframe)
        if df is None or df.empty:
            await update.effective_message.reply_text(f"❌ Data kosong / pair `{symbol}` tidak valid.", parse_mode='Markdown')
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
        report = Formatter.format_signal_message(symbol, price, signal, indicators, confidence)
        await update.effective_message.reply_text(report, parse_mode='Markdown')

    except Exception as e:
        logger.error(e)
        await update.effective_message.reply_text(f"❌ ERROR: {e}")


# ================= SMART CHAT HANDLER =================
# Ketik nama coin saja (btc, eth, sol) -> langsung dapat analisa signal
KNOWN_COINS = {
    'btc', 'eth', 'bnb', 'sol', 'xrp', 'doge', 'ada', 'avax',
    'dot', 'matic', 'link', 'ltc', 'trx', 'near', 'atom', 'uni',
    'pepe', 'shib', 'floki', 'arb', 'op', 'apt', 'sui', 'inj',
    'ton', 'wld', 'fet', 'agix', 'render', 'not', 'mnt',
}

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text.strip().lower()

    # Check if user typed a coin name or pair
    possible_coin = text.replace("/usdt", "").replace("usdt", "").replace("/", "").strip()

    if possible_coin in KNOWN_COINS or (len(possible_coin) >= 2 and len(possible_coin) <= 10 and possible_coin.isalpha()):
        symbol = normalize_symbol(possible_coin)
        await update.effective_message.reply_text(f"⏳ Analisa *{symbol}*...", parse_mode='Markdown')

        try:
            df = await bybit.fetch_ohlcv(symbol, timeframe='5m')
            if df is None or df.empty:
                # Try getting ticker at least
                ticker = await bybit.fetch_ticker(symbol)
                if ticker:
                    change = ticker['change_24h']
                    arrow = "🟢" if change >= 0 else "🔴"
                    sign = "+" if change >= 0 else ""
                    await update.effective_message.reply_text(
                        f"💰 *{ticker['symbol']}*\nHarga: `${ticker['price']:,.4f}` {arrow} `{sign}{change:.2f}%`",
                        parse_mode='Markdown'
                    )
                else:
                    await update.effective_message.reply_text(f"❌ Pair `{symbol}` tidak ditemukan. Ketik /help untuk melihat cara penggunaan.", parse_mode='Markdown')
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
            report = Formatter.format_signal_message(symbol, price, signal, indicators, confidence)
            await update.effective_message.reply_text(report, parse_mode='Markdown')

        except Exception as e:
            logger.error(e)
            await update.effective_message.reply_text(f"❌ ERROR: {e}")
    else:
        await update.effective_message.reply_text(
            f"🤖 Ketik nama coin untuk analisa, contoh:\n`btc` `eth` `sol` `xrp`\n\nAtau gunakan /help untuk lihat semua fitur.",
            parse_mode='Markdown'
        )