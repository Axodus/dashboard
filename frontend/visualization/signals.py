import pandas_ta as ta  # noqa: F401
import plotly.graph_objects as go
import pandas as pd


from frontend.visualization import theme


def get_signal_traces(buy_signals, sell_signals):
    tech_colors = theme.get_color_scheme()
    traces = [
        go.Scatter(x=buy_signals.index, y=buy_signals['close'], mode='markers',
                   marker=dict(color=tech_colors['buy_signal'], size=10, symbol='triangle-up'),
                   name='Buy Signal'),
        go.Scatter(x=sell_signals.index, y=sell_signals['close'], mode='markers',
                   marker=dict(color=tech_colors['sell_signal'], size=10, symbol='triangle-down'),
                   name='Sell Signal')
    ]
    return traces

# Function to generate WhiteRabbit signals
def get_whiterabbit_signal_traces(df, bb_length, bb_std, bb_long_threshold, bb_short_threshold,
                                  rsi_length, rsi_oversold, rsi_overbought):

    # Add Bollinger Bands and RSI indicators
    df.ta.bbands(length=bb_length, std=bb_std, append=True)
    df.ta.rsi(length=rsi_length, overbought=rsi_overbought, oversold=rsi_oversold, append=True)

    # Extract indicator values
    bbp = df[f"BBP_{bb_length}_{bb_std}"]
    rsi = df[f"RSI_{rsi_length}"] # alternatively _{rsi_overbought}_{rsi_oversold}

    # Generate normal buy and sell signals
    buy_signals = df[(bbp < bb_long_threshold) & (rsi < rsi_oversold)]
    sell_signals = df[(bbp > bb_short_threshold) & (rsi > rsi_overbought)]

    # Return signal traces
    return get_signal_traces(buy_signals, sell_signals)




def get_bollinger_v1_signal_traces(df, bb_length, bb_std, bb_long_threshold, bb_short_threshold):
    # Add Bollinger Bands
    candles = df.copy()
    candles.ta.bbands(length=bb_length, std=bb_std, append=True)

    # Generate conditions
    buy_signals = candles[candles[f"BBP_{bb_length}_{bb_std}"] < bb_long_threshold]
    sell_signals = candles[candles[f"BBP_{bb_length}_{bb_std}"] > bb_short_threshold]

    return get_signal_traces(buy_signals, sell_signals)


def get_macdbb_v1_signal_traces(df, bb_length, bb_std, bb_long_threshold, bb_short_threshold, macd_fast, macd_slow,
                                macd_signal):
    # Add Bollinger Bands
    df.ta.bbands(length=bb_length, std=bb_std, append=True)
    # Add MACD
    df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal, append=True)
    # Decision Logic
    bbp = df[f"BBP_{bb_length}_{bb_std}"]
    macdh = df[f"MACDh_{macd_fast}_{macd_slow}_{macd_signal}"]
    macd = df[f"MACD_{macd_fast}_{macd_slow}_{macd_signal}"]

    buy_signals = df[(bbp < bb_long_threshold) & (macdh > 0) & (macd < 0)]
    sell_signals = df[(bbp > bb_short_threshold) & (macdh < 0) & (macd > 0)]

    return get_signal_traces(buy_signals, sell_signals)


def get_supertrend_v1_signal_traces(df, length, multiplier, percentage_threshold):
    # Add indicators
    df.ta.supertrend(length=length, multiplier=multiplier, append=True)
    df["percentage_distance"] = abs(df["close"] - df[f"SUPERT_{length}_{multiplier}"]) / df["close"]

    # Generate long and short conditions
    buy_signals = df[(df[f"SUPERTd_{length}_{multiplier}"] == 1) & (df["percentage_distance"] < percentage_threshold)]
    sell_signals = df[(df[f"SUPERTd_{length}_{multiplier}"] == -1) & (df["percentage_distance"] < percentage_threshold)]

    return get_signal_traces(buy_signals, sell_signals)

# RSI-based signal function
def get_rsi_signal_traces(df, rsi_length, rsi_oversold, rsi_overbought):
    df.ta.rsi(length=rsi_length, append=True)
    rsi = f"RSI_{rsi_length}"
    buy_signals = df[df[rsi] < rsi_oversold]
    sell_signals = df[df[rsi] > rsi_overbought]
    return get_signal_traces(buy_signals, sell_signals)

# Candlestick pattern-based signal function
def get_candlestick_signal_traces(df):
    df['bullish_engulfing'] = (df['open'].shift(1) > df['close'].shift(1)) & (df['open'] < df['close'])
    df['bearish_engulfing'] = (df['open'].shift(1) < df['close'].shift(1)) & (df['open'] > df['close'])
    
    buy_signals = df[df['bullish_engulfing']]
    sell_signals = df[df['bearish_engulfing']]
    
    return get_signal_traces(buy_signals, sell_signals)

# Volume avg signals
def get_volume_avg_traces(df, volume, vol_ma=21):

    df["vol_ma"] = df["volume"].rolling(window=vol_ma).mean()  # Volume moving average
    volume_above_avg = df["volume"] > df["vol_ma"]

    # Generate inverse signals
    outside_upper_band = df["close"] > df[bbu_col]
    outside_lower_band = df["close"] < df[bbl_col]
    inverse_buy_signals = df[outside_lower_band & (~volume_above_avg)]
    inverse_sell_signals = df[outside_upper_band & (~volume_above_avg)]

    # Combine and sort signals
    buy_signals = pd.concat([buy_signals, inverse_buy_signals]).sort_index()
    sell_signals = pd.concat([sell_signals, inverse_sell_signals]).sort_index()