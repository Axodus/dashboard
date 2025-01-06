import importlib
import os

import pandas_ta as ta  # noqa: F401
import streamlit as st
from plotly.subplots import make_subplots

from frontend.components.backtesting import backtesting_section
from frontend.components.config_loader import get_default_config_loader
from frontend.components.save_config import render_save_config
from frontend.pages.config.utils import get_candles
from frontend.st_utils import get_backend_api_client, initialize_st_page
from frontend.visualization import theme
from frontend.visualization.backtesting import create_backtesting_figure
from frontend.visualization.backtesting_metrics import render_accuracy_metrics, render_backtesting_metrics, render_close_types
from frontend.visualization.candles import get_candlestick_trace
from frontend.visualization.utils import add_traces_to_fig

# Initialize the Streamlit page
initialize_st_page(title="Analyzer", icon="", initial_sidebar_state="expanded")

# Load backend client
backend_api_client = get_backend_api_client()

st.text("Analyze and backtest trading strategies dynamically.")

# Discover configuration modules dynamically
def discover_config_modules(config_path="frontend/pages/config"):
    config_modules = []
    for item in os.listdir(config_path):
        if os.path.isdir(os.path.join(config_path, item)) and os.path.isfile(os.path.join(config_path, item, "user_inputs.py")):
            config_modules.append(item)
    return config_modules

# Config loader selection
config_loader_options = discover_config_modules()
selected_config_loader = st.selectbox("Select Strategy", config_loader_options)

# Dynamically import the selected user_inputs module
user_inputs_module = importlib.import_module(f"frontend.pages.config.{selected_config_loader}.user_inputs")
user_inputs = user_inputs_module.user_inputs

config_loader = get_default_config_loader(selected_config_loader)
inputs = user_inputs()
st.session_state["default_config"].update(inputs)

# Visualization section
st.write("### Strategy Signal Visualization")
days_to_visualize = st.number_input("Days to Visualize", min_value=1, max_value=365, value=7)

# Fetch candle data
candles = get_candles(
    connector_name=inputs["candles_connector"],
    trading_pair=inputs["candles_trading_pair"],
    interval=inputs["interval"],
    days=days_to_visualize
)

# Create a multi-row plot for visualization
fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    vertical_spacing=0.02, subplot_titles=(
        'Candlestick Chart', 'Volume', 'Additional Indicators'
    ),
    row_heights=[0.7, 0.2, 0.2]
)

# Add candlestick plot
add_traces_to_fig(fig, [get_candlestick_trace(candles)], row=1, col=1)

# Dynamically load and apply strategy-specific visualizations
try:
    strategy_visualization_module = importlib.import_module(f"frontend.pages.config.{selected_config_loader}.visualization")
    strategy_add_traces = strategy_visualization_module.add_strategy_traces
    strategy_add_traces(fig, candles, inputs)  # Pass fig, candles, and inputs to strategy-specific function
except ModuleNotFoundError:
    st.warning(f"Visualization module for {selected_config_loader} not found. Default visualizations applied.")

# Apply theme and display chart
fig.update_layout(**theme.get_default_layout())
st.plotly_chart(fig, use_container_width=True)

# Backtesting section
bt_results = backtesting_section(inputs, backend_api_client)
if bt_results:
    # Render backtesting metrics and chart
    fig = create_backtesting_figure(
        df=bt_results["processed_data"],
        executors=bt_results["executors"],
        config=inputs
    )
    c1, c2 = st.columns([0.9, 0.1])
    with c1:
        render_backtesting_metrics(bt_results["results"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        render_accuracy_metrics(bt_results["results"])
        st.write("---")
        render_close_types(bt_results["results"])

# Config save section
st.write("---")
render_save_config(st.session_state["default_config"]["id"], st.session_state["default_config"])
