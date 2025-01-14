import pandas_ta as ta  # noqa: F401
import streamlit as st
from plotly.subplots import make_subplots

from frontend.components.backtesting import backtesting_section
from frontend.components.config_loader import get_default_config_loader
from frontend.components.save_config import render_save_config
from frontend.pages.config.utils import get_candles
from frontend.pages.config.whiterabbit_v1.user_inputs import user_inputs
from frontend.st_utils import get_backend_api_client, initialize_st_page
from frontend.visualization import theme
from frontend.visualization.backtesting import create_backtesting_figure
from frontend.visualization.backtesting_metrics import render_accuracy_metrics, render_backtesting_metrics, render_close_types
from frontend.visualization.candles import get_candlestick_trace
from frontend.visualization.indicators import get_bbands_traces, get_rsi_traces, get_volume_trace
from frontend.visualization.logo import logo
from frontend.visualization.signals import get_whiterabbit_signal_traces
from frontend.visualization.utils import add_traces_to_fig

logo()
# Initialize the Streamlit page
initialize_st_page(title="WhiteRabbit V1", icon="🐇", initial_sidebar_state="expanded")
backend_api_client = get_backend_api_client()

st.text("This tool will let you create a config for WhiteRabbit V1 and visualize the strategy.")
get_default_config_loader("whiterabbit_v1")

# Get user inputs (pass the 'candles' DataFrame directly)
inputs = user_inputs()
st.session_state["default_config"].update(inputs)

st.write("### Visualizing WhiteRabbit Signals")
days_to_visualize = st.number_input("Days to Visualize", min_value=1, max_value=365, value=7)

# Load candle data
candles = get_candles(
    connector_name=inputs["candles_connector"],
    trading_pair=inputs["candles_trading_pair"],
    interval=inputs["interval"],
    days=days_to_visualize)

# Create a subplot with 3 rows
fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                    vertical_spacing=0.02, subplot_titles=('Candlestick with Bollinger Bands', 'Volume', "RSI"),
                    row_heights=[0.8, 0.2, 0.2])

# Add traces to the figure
add_traces_to_fig(fig, [get_candlestick_trace(candles)], row=1, col=1)
add_traces_to_fig(fig, get_bbands_traces(candles, inputs["bb_length"], inputs["bb_std"]), row=1, col=1)
# Corrected function call with all required arguments
add_traces_to_fig(fig, get_whiterabbit_signal_traces(
    candles,
    inputs["bb_length"],            # Bollinger Bands length
    inputs["bb_std"],               # Bollinger Bands std dev
    inputs["bb_long_threshold"],    # Long threshold for Bollinger Bands
    inputs["bb_short_threshold"],   # Short threshold for Bollinger Bands
    inputs["rsi_length"],           # RSI length
    inputs["rsi_oversold"],         # RSI oversold threshold
    inputs["rsi_overbought"]        # RSI overbought threshold
), row=1, col=1)

add_traces_to_fig(fig, [get_volume_trace(candles)], row=2, col=1)
add_traces_to_fig(fig, get_rsi_traces(
    candles,
    inputs["rsi_length"],           # RSI length
    inputs["rsi_oversold"],         # RSI oversold threshold
    inputs["rsi_overbought"]        # RSI overbought threshold
), row=3, col=1)


# Update layout and display the figure
fig.update_layout(**theme.get_default_layout())
st.plotly_chart(fig, use_container_width=True)

# Backtesting Section
bt_results = backtesting_section(inputs, backend_api_client)
if bt_results:
    fig = create_backtesting_figure(
        df=bt_results["processed_data"],
        executors=bt_results["executors"],
        config=inputs)
    c1, c2 = st.columns([0.9, 0.1])
    with c1:
        render_backtesting_metrics(bt_results["results"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        render_accuracy_metrics(bt_results["results"])
        st.write("---")
        render_close_types(bt_results["results"])

st.write("---")
render_save_config(st.session_state["default_config"]["id"], st.session_state["default_config"])
