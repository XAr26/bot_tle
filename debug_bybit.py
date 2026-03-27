import asyncio
import ccxt.async_support as ccxt
import traceback

async def run():
    exchange = ccxt.bybit({
        'enableRateLimit': True,
        'hostname': 'bytick.com'
    })
    try:
        await exchange.load_markets()
        print("Loaded!")
    except Exception as e:
        with open('err.log', 'w', encoding='utf-8') as f:
            f.write(traceback.format_exc())
    finally:
        await exchange.close()

asyncio.run(run())
