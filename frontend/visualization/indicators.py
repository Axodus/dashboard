import pandas as pd
import pandas_ta as ta  # noqa: F401
import plotly.graph_objects as go

from frontend.visualization import theme


def get_bbands_traces(df, bb_length, bb_std):
    tech_colors = theme.get_color_scheme()
    df.ta.bbands(length=bb_length, std=bb_std, append=True)
    bb_lower = f'BBL_{bb_length}_{bb_std}'
    bb_middle = f'BBM_{bb_length}_{bb_std}'
    bb_upper = f'BBU_{bb_length}_{bb_std}'
    traces = [
        go.Scatter(x=df.index, y=df[bb_upper], line=dict(color=tech_colors['upper_band']),
                   name='Upper Band'),
        go.Scatter(x=df.index, y=df[bb_middle], line=dict(color=tech_colors['middle_band']),
                   name='Middle Band'),
        go.Scatter(x=df.index, y=df[bb_lower], line=dict(color=tech_colors['lower_band']),
                   name='Lower Band'),
    ]
    return traces


def get_volume_trace(df):
    df.index = pd.to_datetime(df.timestamp, unit='s')
    return go.Bar(x=df.index, y=df['volume'], name="Volume", marker_color=theme.get_color_scheme()["volume"],
                  opacity=0.7)


def get_macd_traces(df, macd_fast, macd_slow, macd_signal):
    tech_colors = theme.get_color_scheme()
    df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal, append=True)
    macd = f'MACD_{macd_fast}_{macd_slow}_{macd_signal}'
    macd_s = f'MACDs_{macd_fast}_{macd_slow}_{macd_signal}'
    macd_hist = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal}'
    traces = [
        go.Scatter(x=df.index, y=df[macd], line=dict(color=tech_colors['macd_line']),
                   name='MACD Line'),
        go.Scatter(x=df.index, y=df[macd_s], line=dict(color=tech_colors['macd_signal']),
                   name='MACD Signal'),
        go.Bar(x=df.index, y=df[macd_hist], name='MACD Histogram',
               marker_color=df[f"MACDh_{macd_fast}_{macd_slow}_{macd_signal}"].apply(
                   lambda x: '#FF6347' if x < 0 else '#32CD32'))
    ]
    return traces


def get_supertrend_traces(df, length, multiplier):
    tech_colors = theme.get_color_scheme()
    df.ta.supertrend(length=length, multiplier=multiplier, append=True)
    supertrend_d = f'SUPERTd_{length}_{multiplier}'
    supertrend = f'SUPERT_{length}_{multiplier}'
    df = df[df[supertrend] > 0]

    # Create segments for line with different colors
    segments = []
    current_segment = {"x": [], "y": [], "color": None}

    for i in range(len(df)):
        if i == 0 or df[supertrend_d].iloc[i] == df[supertrend_d].iloc[i - 1]:
            current_segment["x"].append(df.index[i])
            current_segment["y"].append(df[supertrend].iloc[i])
            current_segment["color"] = tech_colors['buy'] if df[supertrend_d].iloc[i] == 1 else tech_colors['sell']
        else:
            segments.append(current_segment)
            current_segment = {"x": [df.index[i - 1], df.index[i]],
                               "y": [df[supertrend].iloc[i - 1], df[supertrend].iloc[i]],
                               "color": tech_colors['buy'] if df[supertrend_d].iloc[i] == 1 else tech_colors['sell']}

    segments.append(current_segment)

    # Create traces from segments
    traces = [
        go.Scatter(
            x=segment["x"],
            y=segment["y"],
            mode='lines',
            line=dict(color=segment["color"], width=2),
            name='SuperTrend'
        ) for segment in segments
    ]

    return traces

# Function to get RSI traces
def get_rsi_traces(df, rsi_length, rsi_oversold, rsi_overbought):
    # Validate inputs
    if df.empty:
        raise ValueError("Input DataFrame is empty. Cannot calculate RSI.")
    if len(df) < rsi_length:
        raise ValueError(f"Not enough data points. Requires at least {rsi_length} rows.")
    
    # Ensure color scheme exists
    tech_colors = theme.get_color_scheme() if theme else {'rsi_line': '#034efc'}

    # Calculate RSI and validate column existence
    df.ta.rsi(length=rsi_length, append=True)
    rsi_column = f"RSI_{rsi_length}"
    if rsi_column not in df.columns:
        raise ValueError(f"RSI column {rsi_column} not found in DataFrame. Ensure RSI is calculated correctly.")

    # Generate traces
    traces = [
        go.Scatter(x=df.index, y=df[rsi_column], line=dict(color=tech_colors['rsi_line']), name='RSI'),
        go.Scatter(x=df.index, y=[rsi_oversold] * len(df), line=dict(color='green', dash='dash'), name='RSI Oversold'),
        go.Scatter(x=df.index, y=[rsi_overbought] * len(df), line=dict(color='red', dash='dash'), name='RSI Overbought')
    ]
    return traces