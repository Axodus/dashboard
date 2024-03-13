import time
from typing import Optional

import pandas as pd
from pydantic import Field

from hummingbot.smart_components.executors.position_executor.position_executor import PositionExecutor
from hummingbot.smart_components.order_level_distributions.order_level_builder import OrderLevel
from hummingbot.smart_components.strategy_frameworks.directional_trading.directional_trading_controller_base import (
    DirectionalTradingControllerBase,
    DirectionalTradingControllerConfigBase,
)
class WhiterabbitConfig(DirectionalTradingControllerConfigBase):
    strategy_name: str = "whiterabbit"
    bb_length: int = Field(default=10, ge=10, le=200)
    bb_std: float = Field(default=2.0, ge=2.0, le=3.0)
    bb_long_threshold: float = Field(default=-2.0, ge=-2.0, le=0.0)
    bb_short_threshold: float = Field(default=2.0, ge=0.0, le=2.0)
    rsi_length: int = Field(default=7, ge=5, le=10)

class WhiterabbitController(DirectionalTradingControllerBase):  
    def __init__(self, config: WhiterabbitConfig):
        super().__init__(config)
        self.config = config

    def early_stop_condition(self, executor: PositionExecutor, order_level: OrderLevel) -> bool:
        """
        If an executor has an active position, should we close it based on a condition.
        """
        return False

    def cooldown_condition(self, executor: PositionExecutor, order_level: OrderLevel) -> bool:
        """
        After finishing an order, the executor will be in cooldown for a certain amount of time.
        This prevents the executor from creating a new order immediately after finishing one and execute a lot
        of orders in a short period of time from the same side.
        """        
        if executor.close_timestamp and executor.close_timestamp + order_level.cooldown_time > time.time():
            return True
        return False

    def get_processed_data(self) -> pd.DataFrame:
        df = self.candles[0].candles_df
        
        # add indicators
        df.ta.bbands(length=self.config.bb_length, std=self.config.bb_std, append=True)
        df.ta.rsi(length=self.config.rsi_length, append=True)
        bbp = df[f"BBP_{self.config.bb_length}_{self.config.bb_std}"]
        rsi = df[f"RSI_{self.config.rsi_length}"]

        df = self.bbands_signal(df)
        df = self.rsi_signal(df)
        df = self.trailing_stop_signal(df)

        # Generate signal
        long_condition = (bbp < self.config.bb_long_threshold) & (rsi < 15) 
        short_condition = (bbp > self.config.bb_short_threshold) & (rsi > 85)
        df["signal"] = 0
        df.loc[long_condition, "signal"] = 1
        df.loc[short_condition, "signal"] = -1

        return df

    def extra_columns_to_show(self):
        return [f"BBP_{self.config.bb_length}_{self.config.bb_std}",
                f"RSI_{self.config.rsi_length}"]
