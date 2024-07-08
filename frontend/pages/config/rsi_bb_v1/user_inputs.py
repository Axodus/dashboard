import streamlit as st
from frontend.components.directional_trading_general_inputs import get_directional_trading_general_inputs
from frontend.components.risk_management import get_risk_management_inputs

def user_inputs():
    default_config = st.session_state.get("default_config", {})
    bb_length = default_config.get("bb_length", 100)
    bb_std = default_config.get("bb_std", 2.0)
    bb_long_threshold = default_config.get("bb_long_threshold", 0.0)
    bb_short_threshold = default_config.get("bb_short_threshold", 1.0)
    
    rsi_period = default_config.get("rsi_period", 7)
    rsi_overbought = default_config.get("rsi_overbought", 80)
    rsi_oversold = default_config.get("rsi_oversold", 20)

    connector_name, trading_pair, leverage, total_amount_quote, max_executors_per_side, cooldown_time, position_mode, candles_connector_name, candles_trading_pair, interval = get_directional_trading_general_inputs()
    sl, tp, time_limit, ts_ap, ts_delta, take_profit_order_type = get_risk_management_inputs()

    with st.expander("RSI Bollinger Configuration", expanded=True):
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        with c1:
            bb_length = st.number_input("Bollinger Bands Length", min_value=5, max_value=1000, value=bb_length)
        with c2:
            bb_std = st.number_input("Standard Deviation Multiplier", min_value=1.0, max_value=5.0, value=bb_std)
        with c3:
            bb_long_threshold = st.number_input("Long Threshold", value=bb_long_threshold)
        with c4:
            bb_short_threshold = st.number_input("Short Threshold", value=bb_short_threshold)
        with c5:
            rsi_period = st.number_input("RSI Length", min_value=1, max_value=100, value=rsi_period)
        with c6:
            rsi_overbought = st.number_input("RSI Overbought Level", min_value=50, max_value=100, value=rsi_overbought)
        with c7:
            rsi_oversold = st.number_input("RSI Oversold Level", min_value=0, max_value=50, value=rsi_oversold)

    return {
        "controller_name": "rsi_bb_v1",
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
        "rsi_period": rsi_period,
        "rsi_overbought": rsi_overbought,
        "rsi_oversold": rsi_oversold,
        "stop_loss": sl,
        "take_profit": tp,
        "time_limit": time_limit,
        "trailing_stop": {
            "activation_price": ts_ap,
            "trailing_delta": ts_delta
        },
        "take_profit_order_type": take_profit_order_type.value
    }
