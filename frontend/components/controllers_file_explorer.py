from streamlit_elements import mui
import constants
from frontend.components.file_explorer_base import FileExplorerBase
import os

class ControllersFileExplorer(FileExplorerBase):
    def add_tree_view(self):
        def list_controllers_by_directory(base_path):
            controllers_by_directory = {}
            for root, dirs, files in os.walk(base_path):
                # Filter Python files and skip __init__.py
                py_files = [f for f in files if f.endswith(".py") and f != "__init__.py"]
                if py_files:
                    # Get relative directory name
                    relative_dir = os.path.relpath(root, base_path)
                    controllers_by_directory[relative_dir] = py_files
            return controllers_by_directory

        # Get controllers grouped by directory
        controllers_by_directory = list_controllers_by_directory(constants.CONTROLLERS_PATH)

        with mui.lab.TreeView(
            defaultExpandIcon=mui.icon.ChevronRight,
            defaultCollapseIcon=mui.icon.ExpandMore,
            onNodeSelect=lambda event, node_id: self.set_selected_file(event, node_id),
        ):
            for directory, files in controllers_by_directory.items():
                # Add a tree item for each directory
                with mui.lab.TreeItem(nodeId=directory, label=f"📁 {directory}"):
                    for file_name in files:
                        # Create a tree item for each Python file within the directory
                        mui.lab.TreeItem(
                            nodeId=f"{constants.CONTROLLERS_PATH}/{directory}/{file_name}",
                            label=f"🐍 {file_name[:-3]}"  # Strip .py extension
                        )
