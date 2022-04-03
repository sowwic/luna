import os
from PySide2 import QtWidgets
import luna
import luna.utils.pysideFn as pysideFn
import luna_rig.functions.asset_files as asset_files


class FileMenu(QtWidgets.QMenu):
    def __init__(self, main_window, parent=None):
        super(FileMenu, self).__init__("File", parent)
        self.main_window = main_window
        self.workspace_widget = main_window.workspace_wgt

        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        self.recent_projects_menu = QtWidgets.QMenu("Recent projects")

    def create_actions(self):
        self.model_reference_action = QtWidgets.QAction(pysideFn.get_QIcon("reference.svg", maya_icon=True), "Reference model", self)
        self.clear_referances_action = QtWidgets.QAction(pysideFn.get_QIcon("unloadedReference.png", maya_icon=True), "Clear all references", self)
        self.save_new_skeleton_action = QtWidgets.QAction("Increment and save", self)
        self.save_skeleton_as_action = QtWidgets.QAction("Save skeleton as...", self)
        self.save_rig_as_action = QtWidgets.QAction("Save rig as...", self)
        # Build
        self.new_build_action = QtWidgets.QAction('New Build...', self)
        self.open_build_file_action = QtWidgets.QAction("Open Build...", self)
        self.open_build_tab_action = QtWidgets.QAction('Open Build As Tab', self)
        self.save_build_action = QtWidgets.QAction('Save Build', self)
        self.save_build_as_action = QtWidgets.QAction("Save Build As...", self)

        # Shortcuts
        self.new_build_action.setShortcut('Ctrl+N')
        self.open_build_file_action.setShortcut('Ctrl+O')
        self.open_build_tab_action.setShortcut('Ctrl+Shift+O')
        self.save_build_action.setShortcut('Ctrl+S')
        self.save_build_as_action.setShortcut('Ctrl+Shift+S')

    def create_connections(self):
        self.main_window.mdi_area.subWindowActivated.connect(self.update_actions_state)
        self.aboutToShow.connect(self.update_recent_projects)
        self.aboutToShow.connect(self.update_actions_state)
        # Actions
        self.model_reference_action.triggered.connect(asset_files.reference_model)
        self.clear_referances_action.triggered.connect(asset_files.clear_all_references)
        self.save_new_skeleton_action.triggered.connect(lambda: asset_files.increment_save_file(typ="skeleton"))
        self.save_skeleton_as_action.triggered.connect(lambda: asset_files.save_file_as(typ="skeleton"))
        self.save_rig_as_action.triggered.connect(lambda: asset_files.save_file_as(typ="rig"))
        self.save_new_skeleton_action.triggered.connect(self.workspace_widget.update_data)
        # Build actions
        self.new_build_action.triggered.connect(self.main_window.on_build_new)
        self.open_build_file_action.triggered.connect(self.main_window.on_build_open)
        self.open_build_tab_action.triggered.connect(self.main_window.on_build_open_tabbed)
        self.save_build_action.triggered.connect(self.main_window.on_build_save)
        self.save_build_as_action.triggered.connect(self.main_window.on_build_save_as)

    def populate(self):
        self.addSection("Project")
        self.addMenu(self.recent_projects_menu)
        self.addSection("Build graph")
        self.addAction(self.new_build_action)
        self.addAction(self.open_build_file_action)
        self.addAction(self.open_build_tab_action)
        self.addAction(self.save_build_action)
        self.addAction(self.save_build_as_action)
        self.addSection("Skeleton")
        self.addAction(self.save_skeleton_as_action)
        self.addAction(self.save_new_skeleton_action)
        self.addSection("Rig")
        self.addAction(self.save_rig_as_action)
        self.addSection("Asset")
        self.addAction(self.model_reference_action)
        self.addAction(self.clear_referances_action)

    def update_recent_projects(self):
        projects_data = luna.Config.get(luna.ProjectVars.recent_projects)

        self.recent_projects_menu.clear()
        for prj in projects_data:
            if not os.path.isdir(prj[1]):
                continue
            project_action = QtWidgets.QAction(prj[0], self)
            project_action.setToolTip(prj[1])
            project_action.triggered.connect(lambda path=prj[1], *args: self.workspace_widget.project_grp.set_project(path))
            self.recent_projects_menu.addAction(project_action)

    def update_actions_state(self):
        is_asset_set = True if luna.workspace.Asset.get() else False
        is_current_editor = self.main_window.current_editor is not None
        self.model_reference_action.setEnabled(is_asset_set)
        self.save_skeleton_as_action.setEnabled(is_asset_set)
        self.save_new_skeleton_action.setEnabled(is_asset_set)
        self.save_rig_as_action.setEnabled(is_asset_set)
        self.open_build_file_action.setEnabled(is_asset_set)
        self.open_build_tab_action.setEnabled(is_asset_set)
        self.save_build_action.setEnabled(is_asset_set and is_current_editor)
        self.save_build_as_action.setEnabled(is_asset_set and is_current_editor)
