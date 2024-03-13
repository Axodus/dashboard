import time
import pandas as pd
from pydantic import Field
import pandas_ta as ta
from decimal import Decimal
from typing import Dict
import inspect
import os
import importlib.util

from hummingbot.connector.connector_base import ConnectorBase, TradeType
from hummingbot.core.data_type.common import OrderType
from hummingbot.data_feed.candles_feed.candles_factory import CandlesConfig
from hummingbot.smart_components.executors.position_executor.position_executor import PositionExecutor

from hummingbot.smart_components.controllers.whiterabbit import Whiterabbit, WhiterabbitConfig

from hummingbot.smart_components.strategy_frameworks.directional_trading.directional_trading_controller_base import (
    DirectionalTradingControllerBase,
    DirectionalTradingControllerConfigBase,
)
from hummingbot.smart_components.strategy_frameworks.data_types import (
    ExecutorHandlerStatus,
    OrderLevel,
    TripleBarrierConf,
)
from hummingbot.smart_components.strategy_frameworks.directional_trading.directional_trading_executor_handler import (
    DirectionalTradingExecutorHandler,
)
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase

class WhiterabbitConfig(DirectionalTradingControllerConfigBase):
    strategy_name: str = "whiterabbit"
    
    bb_length: int = Field(default=10, ge=10, le=200)
    bb_std: float = Field(default=2.0, ge=2.0, le=3.0)
    bb_long_threshold: float = Field(default=-2.0, ge=-2.0, le=0.0)
    bb_short_threshold: float = Field(default=2.0, ge=0.0, le=2.0)
    rsi_length: int = Field(default=7, ge=5, le=10)

class Whiterabbit(ScriptStrategyBase):

    def __init__(self, config: WhiterabbitConfig):
        super().__init__(config)
        self.config = config

    def cooldown_condition(self, executor: PositionExecutor, order_level: OrderLevel) -> bool:
        """
        After finishing an order, the executor will be in cooldown for a certain amount of time.
        This prevents the executor from creating a new order immediately after finishing one and execute a lot
        of orders in a short period of time from the same side.
        """
        return executor.close_timestamp and executor.close_timestamp + order_level.cooldown_time > time.time()

    def early_stop_condition(self, executor: PositionExecutor, order_level: OrderLevel) -> bool:
        """
        If an executor has an active position, should we close it based on a condition.
        """
        return False
    
    def trailing_stop_signal(self, df, trailing_stop_percent=0.60):
        # Implement trailing stop logic
        df["trailing_stop"] = df["close"] * (1 - trailing_stop_percent / 100)
        # Generate signals based on trailing stop
        df["trailing_stop_signal"] = 0
        # Long signal: Close below trailing stop
        df.loc[df["close"] < df["trailing_stop"], "trailing_stop_signal"] = 1
        # Short signal: Close above trailing stop
        df.loc[df["close"] > df["trailing_stop"], "trailing_stop_signal"] = -1

        return df

    def bbands_signal(self, df):
        # Calculate Bollinger Bands
        df.ta.bbands(length=self.config.bb_length, std=self.config.bb_std, append=True)

        # Generate signals based on Bollinger Bands
        df["bb_upper"] = df[f"BBL_{self.config.bb_length}_{self.config.bb_std}"]
        df["bb_lower"] = df[f"BBU_{self.config.bb_length}_{self.config.bb_std}"]
        df["bb_signal"] = 0
        # Long signal: Close below lower Bollinger Band
        df.loc[df["close"] <= df["bb_lower"], "bb_signal"] = 1
        # Short signal: Close above upper Bollinger Band
        df.loc[df["close"] >= df["bb_upper"], "bb_signal"] = -1

        return df

    def rsi_signal(self, df):
        # Calculate Relative Strength Index (RSI)
        df["RSI"] = ta.rsi(df["close"], length=self.config.rsi_length)
        # Generate signals based on RSI
        df["rsi_signal"] = 0
        # Long signal: RSI below 20
        df.loc[df["RSI"] < 15, "rsi_signal"] = 1
        # Short signal: RSI above 80
        df.loc[df["RSI"] > 85, "rsi_signal"] = -1

        return df
    
    def get_processed_data(self) -> pd.DataFrame:
        df = self.candles[0].candles_df
        
        # Add indicators
        df.ta.bbands(length=self.config.bb_length, std=self.config.bb_std, append=True)
        df.ta.rsi(length=self.config.rsi_length, append=True)
        bbp = df[f"BBP_{self.config.bb_length}_{self.config.bb_std}"]
        rsi = df[f"RSI_{self.config.rsi_length}"]

        # Apply strategy logic
        df = self.bbands_signal(df)
        df = self.rsi_signal(df)
        df = self.trailing_stop_signal(df)

        # Combine signals
        long_condition = (bbp < self.config.bb_long_threshold) & (rsi < 15) 
        short_condition = (bbp > self.config.bb_short_threshold) & (rsi > 85)
        df["signal"] = 0
        df.loc[long_condition, "signal"] = 1
        df.loc[short_condition, "signal"] = -1

        return df
    
    def extra_columns_to_show(self):
        return [f"BBP_{self.config.bb_length}_{self.config.bb_std}",
                f"RSI_{self.config.rsi_length}"]
