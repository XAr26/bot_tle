import mplfinance as mpf
import pandas as pd

def generate_chart(df, symbol="BTCUSDT"):
    df = df.copy()

    # rename kolom biar cocok
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })

    df.index = pd.to_datetime(df.index)

    filename = f"{symbol}_chart.png"

    mpf.plot(
        df,
        type='candle',
        volume=True,
        style='yahoo',
        title=f"{symbol} Chart",
        mav=(50, 200),
        savefig=filename
    )

    return filename