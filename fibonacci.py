from binance.client import Client
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'
client = Client(api_key, api_secret)

symbols = ['BTCUSDT', 'AVAXUSDT', 'STRKUSDT']

# Fibonacci levels
fibonacci_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]

def get_fibonacci_levels(lows, highs, trend):
    max_price = max(highs)
    min_price = min(lows)
    
    fibonacci_levels_calculated = [min_price + level * (max_price - min_price) for level in fibonacci_levels]
    
    if trend == 'uptrend':
        levels = fibonacci_levels_calculated
    elif trend == 'downtrend':
        levels = fibonacci_levels_calculated[::-1]
    else:
        levels = fibonacci_levels_calculated

    return levels


for symbol in symbols:
    klines = client.get_klines(symbol=symbol, interval='15m', limit=65)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

    # Convert relevant columns to numeric
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].apply(pd.to_numeric)

    # Perform trend analysis based on closing prices (e.g., using a simple moving average)
    df['MA15'] = df['close'].rolling(window=15).mean()

    # Check the relationship between the last closing price and the 15-day moving average
    last_close = df['close'].iloc[-1]
    last_ma15 = df['MA15'].iloc[-1]

    if last_close > last_ma15:
        trend_direction = 'Up'
        fib_levels = get_fibonacci_levels(df['low'], df['high'], trend_direction)
        min_price = df['low'].min()
        max_price = df['high'].max()
    elif last_close < last_ma15:
        trend_direction = 'Down'
        fib_levels = get_fibonacci_levels(df['low'], df['high'], trend_direction)
        min_price = df['low'].min()
        max_price = df['high'].max()
    else:
        trend_direction = 'Sideways'
        fib_levels = get_fibonacci_levels(df['low'], df['high'], trend_direction)
        min_price = df['low'].min()
        max_price = df['high'].max()

    # Plot the graph as a candlestick chart
    fig, ax = plt.subplots()
    ax.plot(df['timestamp'], df['MA15'], label='15-Day Moving Average', linestyle='-', linewidth=2, color='blue')

    for i in range(len(df)):
        if df['open'][i] < df['close'][i]:
            ax.plot(df['timestamp'][i], df['open'][i], 'g_', markersize=10)  # Green bar for bullish candle
            ax.plot([df['timestamp'][i], df['timestamp'][i]], [df['low'][i], df['open'][i]], 'g-', linewidth=2)
            ax.plot([df['timestamp'][i], df['timestamp'][i]], [df['close'][i], df['high'][i]], 'g-', linewidth=2)
        else:
            ax.plot(df['timestamp'][i], df['open'][i], 'r_', markersize=10)  # Red bar for bearish candle
            ax.plot([df['timestamp'][i], df['timestamp'][i]], [df['high'][i], df['open'][i]], 'r-', linewidth=2)
            ax.plot([df['timestamp'][i], df['timestamp'][i]], [df['open'][i], df['low'][i]], 'r-', linewidth=2)

    # Plot Fibonacci levels
    for level in fib_levels:
        ax.axhline(y=level, color='r', linestyle='--', label=f'Fib {level:.3f}')

    ax.set_title(f'Trading Pair: {symbol}, Trend Direction: {trend_direction}')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')

    plt.legend()
    plt.show()
