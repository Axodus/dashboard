from streamlit_elements import mui

import constants
from backend.utils.os_utils import (
    get_directories_from_directory,
    get_log_files_from_directory,
    get_python_files_from_directory,
    get_yml_files_from_directory,
)
from frontend.components.file_explorer_base import FileExplorerBase


class BotsFileExplorer(FileExplorerBase):
    def add_tree_view(self):
        directory = constants.BOTS_FOLDER
        bots = [bot.split("/")[-1] for bot in get_directories_from_directory(directory) if
                bot not in ["__pycache__", "__init__.py"]]

        with mui.lab.TreeView(
                defaultExpandIcon=mui.icon.ChevronRight,
                defaultCollapseIcon=mui.icon.ExpandMore,
                onNodeSelect=lambda event, node_id: self.set_selected_file(event, node_id)
        ):
            for bot in bots:
                with mui.lab.TreeItem(nodeId=bot, label=f"🤖 {bot}"):

                    # Scripts folder
                    with mui.lab.TreeItem(nodeId=f"scripts_{bot}", label="🐍 Scripts"):
                        scripts_dir = f"{directory}/{bot}/scripts"
                        for file in get_python_files_from_directory(scripts_dir):
                            if not file.endswith(".pyc"):
                                mui.lab.TreeItem(nodeId=file, label=f"📄 {file.split('/')[-1]}")

                    # Conf folder
                    with mui.lab.TreeItem(nodeId=f"conf_{bot}", label="📜 Configuration"):
                        conf_dir = f"{directory}/{bot}/conf"
                        for file in get_yml_files_from_directory(conf_dir):
                            mui.lab.TreeItem(nodeId=file, label=f"📄 {file.split('/')[-1]}")

                    # Logs folder
                    with mui.lab.TreeItem(nodeId=f"logs_{bot}", label="🗄️ Logs"):
                        logs_dir = f"{directory}/{bot}/logs"
                        for file in get_log_files_from_directory(logs_dir):
                            mui.lab.TreeItem(nodeId=file, label=f"📄 {file.split('/')[-1]}")

                    # Data folder
                    data_dir = f"{directory}/{bot}/data"
                    if get_directories_from_directory(data_dir):  # Ensures folder exists
                        with mui.lab.TreeItem(nodeId=f"data_{bot}", label="📊 Data"):
                            for file in get_python_files_from_directory(data_dir):  # Assuming Python files are relevant
                                mui.lab.TreeItem(nodeId=file, label=f"📄 {file.split('/')[-1]}")

                    # Credentials folder
                    credentials_dir = f"{directory}/{bot}/credentials"
                    if get_directories_from_directory(credentials_dir):  # Ensures folder exists
                        with mui.lab.TreeItem(nodeId=f"credentials_{bot}", label="🔒 Credentials"):
                            for file in get_python_files_from_directory(credentials_dir):  # Assuming Python files are relevant
                                mui.lab.TreeItem(nodeId=file, label=f"📄 {file.split('/')[-1]}")
