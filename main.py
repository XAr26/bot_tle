import sys
from dotenv import load_dotenv
# Load environment variables before any other imports that might use them
load_dotenv(override=True)

from telegram.ext import ApplicationBuilder, CommandHandler
from config.config import Config
from telegram.ext import CallbackQueryHandler, MessageHandler, filters
from handlers.command_handlers import button_handler
from handlers.command_handlers import (
    start_handler,
    signal_handler,
    help_handler,
    price_handler,
    auto_on_handler,
    auto_off_handler,
    chat_handler
)
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger()

def main():
    """Start the professional crypto analysis bot."""
    TOKEN = Config.BOT_TOKEN

    if not TOKEN or TOKEN == "your_telegram_bot_token_here":
        logger.error("BOT_TOKEN is missing or not configured in .env file!")
        sys.exit(1)

    try:
        # Create the Application
        app = (
            ApplicationBuilder()
            .token(TOKEN)
            .connect_timeout(30)
            .read_timeout(30)
            .build()
        )

        # Register handlers
        app.add_handler(CommandHandler(["start", "star"], start_handler))
        app.add_handler(CommandHandler("help", help_handler))
        app.add_handler(CommandHandler("signal", signal_handler))
        app.add_handler(CommandHandler("price", price_handler))
        app.add_handler(CommandHandler("auto", auto_on_handler))  # default
        app.add_handler(CommandHandler("auto_on", auto_on_handler))
        app.add_handler(CommandHandler("auto_off", auto_off_handler))
        app.add_handler(CallbackQueryHandler(button_handler))
        
        # Add handler for normal messages
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

        logger.info("Bot starting up...")
        print("BOT IS RUNNING... Press Ctrl+C to stop.")
        
        # Start the bot
        app.run_polling()

    except Exception as e:
      logger.critical(f"FATAL ERROR during bot startup: {e}")
      sys.exit(1)

if __name__ == "__main__":
    main()