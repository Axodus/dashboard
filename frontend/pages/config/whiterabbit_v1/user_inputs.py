import streamlit as st

from frontend.components.directional_trading_general_inputs import get_directional_trading_general_inputs
from frontend.components.risk_management import get_risk_management_inputs


def user_inputs():

    # Fetch the default configuration from session state
    default_config = st.session_state.get("default_config", {})

    # Set default values for Bollinger Bands configuration
    bb_length = default_config.get("bb_length", 100)
    bb_std = default_config.get("bb_std", 2.0)
    bb_long_threshold = default_config.get("bb_long_threshold", 0.0)
    bb_short_threshold = default_config.get("bb_short_threshold", 1.0)

    # Fetch general directional trading inputs
    connector_name, trading_pair, leverage, total_amount_quote, max_executors_per_side, cooldown_time, position_mode, \
        candles_connector_name, candles_trading_pair, interval = get_directional_trading_general_inputs()

    # Fetch risk management inputs
    sl, tp, time_limit, ts_ap, ts_delta, take_profit_order_type = get_risk_management_inputs()

    # Bollinger Bands Configuration Section
    with st.expander("Bollinger Bands Configuration", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            bb_length = st.number_input("Bollinger Bands Length", min_value=5, max_value=1000, value=bb_length)
        with c2:
            bb_std = st.number_input("Standard Deviation Multiplier", min_value=1.0, max_value=5.0, value=bb_std)
        with c3:
            bb_long_threshold = st.number_input("Long Threshold", value=bb_long_threshold)
        with c4:
            bb_short_threshold = st.number_input("Short Threshold", value=bb_short_threshold)

    # RSI Configuration Inputs Section
    with st.expander("RSI Configuration", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            rsi_length = st.number_input("RSI Length", min_value=2, max_value=50, value=3)
        with c2:
            rsi_oversold = st.number_input("RSI Oversold Level", min_value=1, max_value=50, value=10)
        with c3:
            rsi_overbought = st.number_input("RSI Overbought Level", min_value=50, max_value=99, value=95)
       
    # Volume Input Section
    #with st.expander("Volume Configuration", expanded=True):
    #    vol_ma = st.number_input("Volume Moving Average Length", min_value=5, max_value=100, value=21)

    # Return all the collected configuration values in a dictionary format
    return {
        "controller_name": "whiterabbit_v1",
        "controller_type": "directional_trading",
        "connector_name": connector_name,
        "trading_pair": trading_pair,
        "leverage": leverage,
        "total_amount_quote": total_amount_quote,
        "max_executors_per_side": max_executors_per_side,
        "cooldown_time": cooldown_time,
        "position_mode": position_mode,
        "candles_connector": candles_connector_name,
        "candles_trading_pair": candles_trading_pair,
        "interval": interval,
        "bb_length": bb_length,
        "bb_std": bb_std,
        "bb_long_threshold": bb_long_threshold,
        "bb_short_threshold": bb_short_threshold,
        "rsi_length": rsi_length,
        "rsi_oversold": rsi_oversold,
        "rsi_overbought": rsi_overbought,
        "stop_loss": sl,
        "take_profit": tp,
        "time_limit": time_limit,
        "trailing_stop": {
            "activation_price": ts_ap,
            "trailing_delta": ts_delta
        },
        "take_profit_order_type": take_profit_order_type.value
    }
