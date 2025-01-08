import os

from streamlit_elements import lazy, mui

import constants
from backend.utils.file_templates import directional_trading_controller_template
from backend.utils.os_utils import save_file

from .dashboard import Dashboard


class StrategyCreationCard(Dashboard.Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._strategy_name = "CustomStrategy"
        self._strategy_type = "directional_trading"  # Default to an existing type
        self._new_directory_name = ""  # For creating a new directory

    def _set_strategy_name(self, event):
        self._strategy_name = event.target.value

    def _set_strategy_type(self, event):
        try:
            # Extract the selected strategy type
            self._strategy_type = event.get("value")
            if self._strategy_type == "create_new":
                self._new_directory_name = self._strategy_name.lower()
            print(f"Strategy type set to: {self._strategy_type}")
        except AttributeError:
            raise ValueError(f"Invalid event structure: {event}")

    def _create_strategy(self):
        # Validate strategy type
        if not self._strategy_type:
            print("Error: No valid strategy type selected.")
            return

        # Determine target directory
        if self._strategy_type == "create_new":
            if not self._new_directory_name:
                print("Error: Directory name cannot be empty.")
                return
            target_directory = os.path.join(constants.CONTROLLERS_PATH, self._new_directory_name)
        else:
            target_directory = os.path.join(constants.CONTROLLERS_PATH, self._strategy_type)

        # Ensure the directory exists
        os.makedirs(target_directory, exist_ok=True)

        # Generate strategy code
        strategy_code = directional_trading_controller_template(self._strategy_name)

        # Save the strategy file
        file_path = os.path.join(target_directory, f"{self._strategy_name.lower()}.py")
        if os.path.exists(file_path):
            print(f"Error: Strategy file '{file_path}' already exists!")
            return

        try:
            save_file(name=f"{self._strategy_name.lower()}.py", content=strategy_code, path=target_directory)
            print(f"Strategy '{self._strategy_name}' created successfully in '{target_directory}'!")
        except Exception as e:
            print(f"Error creating strategy: {e}")

    def __call__(self):
        with mui.Paper(key=self._key,
                       sx={"display": "flex",
                           "flexDirection": "column",
                           "borderRadius": 3,
                           "overflow": "hidden"}, elevation=1):

            with self.title_bar(padding="10px 15px 10px 15px", dark_switcher=False):
                mui.icon.NoteAdd()
                mui.Typography("Create new strategy", variant="h6")

            with mui.Grid(container=True, spacing=2, sx={"padding": "10px"}):
                # Strategy Type Selection
                with mui.Grid(item=True, sm=12, md=5):
                    with mui.FormControl(variant="standard", sx={"width": "100%"}):
                        mui.FormHelperText("Template name")
                    with mui.Select(
                        label="Select strategy type",
                        defaultValue="directional_trading",
                        variant="standard",
                        onChange=lazy(self._set_strategy_type)
                    ):
                        mui.MenuItem("Directional", value="directional_trading")
                        mui.MenuItem("Generic", value="generic")
                        mui.MenuItem("Market Making", value="market_making")
                        mui.MenuItem("Create New Directory", value="create_new")

                # Strategy Name Input
                with mui.Grid(item=True, sm=12, md=5):
                    with mui.FormControl(variant="standard", sx={"width": "100%"}):
                        mui.TextField(
                            defaultValue="CustomStrategy",
                            label="Strategy Name",
                            variant="standard",
                            onChange=lazy(self._set_strategy_name)
                        )
                # Create Button
                with mui.Grid(item=True, sm=12, md=2):
                    with mui.Button(variant="contained", onClick=self._create_strategy):
                        mui.icon.Add()
                        mui.Typography("Create", variant="body1")
