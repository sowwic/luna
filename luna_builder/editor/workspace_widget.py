import os
import subprocess

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

import pymel.core as pm
import luna
from luna import Config
from luna import Logger
from luna import ProjectVars
from luna.utils import pysideFn
from luna.interface import shared_widgets


class WorkspaceWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(WorkspaceWidget, self).__init__(parent)

        self.label = "Workspace"
        self.setMinimumWidth(315)
        # self.icon = pysideFn.get_QIcon("workspace.png")

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.scroll_wgt = shared_widgets.ScrollWidget()
        self.project_grp = ProjectGroup()
        self.asset_grp = AssetGroup()
        self.scroll_wgt.add_widget(self.project_grp)
        self.scroll_wgt.add_widget(self.asset_grp)
        self.scroll_wgt.content_layout.addStretch()

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scroll_wgt)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.project_grp.project_changed.connect(lambda prj: self.asset_grp.setDisabled(prj is None))
        self.project_grp.project_changed.connect(self.asset_grp.update_asset_data)
        self.project_grp.project_changed.connect(self.asset_grp.update_asset_completion)
        self.project_grp.exit_btn.clicked.connect(self.asset_grp.reset_asset_data)

    def update_data(self):
        self.project_grp.update_project()
        self.asset_grp.update_asset_data()

    def showEvent(self, event):
        super(WorkspaceWidget, self).showEvent(event)
        self.update_data()


class ProjectGroup(QtWidgets.QGroupBox):

    project_changed = QtCore.Signal(luna.workspace.Project)

    def __init__(self, title="Project", parent=None):
        super(ProjectGroup, self).__init__(title, parent)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.name_lineedit = QtWidgets.QLineEdit()
        self.name_lineedit.setReadOnly(True)
        self.set_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("fileOpen", maya_icon=True), "")
        self.set_btn.setToolTip("Set existing project")
        self.create_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("plus.png"), "")
        self.create_btn.setToolTip("Create new project")
        self.exit_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("outArrow.png"), "")
        self.exit_btn.setToolTip("Exit luna workspace")

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(QtWidgets.QLabel("Current:"))
        self.main_layout.addWidget(self.name_lineedit)
        self.main_layout.addWidget(self.create_btn)
        self.main_layout.addWidget(self.set_btn)
        self.main_layout.addWidget(self.exit_btn)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.create_btn.clicked.connect(self.create_project)
        self.set_btn.clicked.connect(self.browse_project)
        self.exit_btn.clicked.connect(self.exit_project)
        self.project_changed.connect(self.update_project)

    def update_project(self):
        current_project = luna.workspace.Project.get()
        if not current_project:
            self.name_lineedit.setText("Not set")
            return

        self.name_lineedit.setText(current_project.name)
        self.name_lineedit.setToolTip(current_project.path)

    def create_project(self):
        prev_project_path = Config.get(ProjectVars.previous_project, default="")
        Logger.debug("Previous project: {0}".format(prev_project_path))
        if os.path.isdir(prev_project_path):
            root_dir = os.path.dirname(prev_project_path)
        else:
            root_dir = ""

        path = QtWidgets.QFileDialog.getExistingDirectory(None, "Create luna project", root_dir)
        if path:
            prj = luna.workspace.Project.create(path)
            self.project_changed.emit(prj)

    def browse_project(self):
        prev_project_path = Config.get(ProjectVars.previous_project, default="")
        Logger.debug("Previous project: {0}".format(prev_project_path))
        if os.path.isdir(prev_project_path):
            root_dir = os.path.dirname(prev_project_path)
        else:
            root_dir = ""

        path = QtWidgets.QFileDialog.getExistingDirectory(None, "Set luna project", root_dir)
        if path:
            self.set_project(path)

    def set_project(self, path):
        prj = luna.workspace.Project.set(path)
        self.project_changed.emit(prj)

    def exit_project(self):
        luna.workspace.Project.exit()
        self.project_changed.emit(None)


class AssetGroup(QtWidgets.QGroupBox):

    ASSET_TYPES = Config.get(luna.LunaVars.asset_types, default=['character'], cached=True)
    # Signals
    asset_changed = QtCore.Signal(object)

    def __init__(self, title="Asset", parent=None):
        super(AssetGroup, self).__init__(title, parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def keyPressEvent(self, event):
        super(AssetGroup, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Enter:
            self.set_asset()

    def create_widgets(self):
        self.asset_type_cmbox = QtWidgets.QComboBox()
        self.asset_type_cmbox.addItems(AssetGroup.ASSET_TYPES)
        self.asset_name_lineedit = QtWidgets.QLineEdit()
        self.asset_name_lineedit.setPlaceholderText("Name")

        self.file_system = QtWidgets.QFileSystemModel()
        self.file_system.setNameFilterDisables(False)
        self.file_tree = QtWidgets.QTreeView()
        self.file_tree.setModel(self.file_system)
        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.setColumnWidth(0, 200)
        self.file_tree.setMinimumWidth(200)
        self.file_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.model_path_wgt = shared_widgets.PathWidget(mode=shared_widgets.PathWidget.Mode.EXISTING_FILE,
                                                        label_text="Model file: ",
                                                        dialog_label="Select model file")
        self.rig_path_wgt = shared_widgets.PathWidget(mode=shared_widgets.PathWidget.Mode.EXISTING_FILE,
                                                      label_text="Latest rig: ")
        self.model_open_btn = QtWidgets.QPushButton("open")
        self.model_reference_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("reference.svg", maya_icon=True), "")
        self.rig_open_btn = QtWidgets.QPushButton("open")
        self.rig_reference_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("reference.svg", maya_icon=True), "")
        self.model_path_wgt.add_widget(self.model_open_btn)
        self.model_path_wgt.add_widget(self.model_reference_btn)
        self.rig_path_wgt.add_widget(self.rig_open_btn)
        self.rig_path_wgt.add_widget(self.rig_reference_btn)
        self.rig_path_wgt.browse_button.hide()

    def create_layouts(self):
        self.basic_info_layout = QtWidgets.QHBoxLayout()
        self.basic_info_layout.setContentsMargins(0, 0, 0, 0)
        # self.basic_info_layout.addWidget(QtWidgets.QLabel("Type:"))
        self.basic_info_layout.addWidget(self.asset_type_cmbox)
        self.basic_info_layout.addWidget(self.asset_name_lineedit)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.basic_info_layout)
        self.main_layout.addWidget(self.file_tree)
        self.main_layout.addWidget(self.model_path_wgt)
        self.main_layout.addWidget(self.rig_path_wgt)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.asset_changed.connect(self.update_asset_data)
        # File
        self.file_tree.doubleClicked.connect(self.open_file)
        self.asset_name_lineedit.returnPressed.connect(self.set_asset)
        self.asset_type_cmbox.currentIndexChanged.connect(self.update_asset_completion)
        self.model_path_wgt.line_edit.textChanged.connect(self.save_model_path)
        self.model_open_btn.clicked.connect(lambda file_type="model", *args: self.open_asset_file(file_type))
        self.model_reference_btn.clicked.connect(lambda file_type="model", ref=True, *args: self.open_asset_file(file_type, reference=ref))
        self.rig_open_btn.clicked.connect(lambda file_type="rig", *args: self.open_asset_file(file_type))
        self.rig_reference_btn.clicked.connect(lambda file_type="rig", ref=True, *args: self.open_asset_file(file_type, reference=ref))
        # Menus
        self.file_tree.customContextMenuRequested.connect(self.file_context_menu)

    @QtCore.Slot()
    def set_asset(self):
        current_project = luna.workspace.Project.get()
        asset_name = self.asset_name_lineedit.text()
        if not current_project or not asset_name:
            return
        asset_type = self.asset_type_cmbox.currentText().lower()
        asset_path = os.path.join(current_project.path, asset_type + "s", asset_name)
        asset_path = os.path.normpath(asset_path)
        if not os.path.isdir(asset_path):
            reply = QtWidgets.QMessageBox.question(self, "Missing asset", "Asset {0} doesn't exist. Create it?".format(asset_name))
            if not reply == QtWidgets.QMessageBox.Yes:
                return
        new_asset = luna.workspace.Asset(current_project, asset_name, asset_type)
        self.asset_changed.emit(new_asset)

    @QtCore.Slot()
    def update_asset_data(self):
        current_project = luna.workspace.Project.get()
        current_asset = luna.workspace.Asset.get()
        if not current_project or not current_asset:
            self.reset_asset_data()
            return

        self.asset_name_lineedit.setText(current_asset.name)
        self.asset_type_cmbox.setCurrentText(current_asset.type)
        self.model_path_wgt.line_edit.setText(current_asset.model_path)
        self.rig_path_wgt.line_edit.setText(current_asset.latest_rig_path)
        self.file_system.setRootPath(current_asset.path)
        self.file_tree.setRootIndex(self.file_system.index(current_asset.path))

    def reset_asset_data(self):
        current_project = luna.workspace.Project.get()
        if not current_project:
            root_path = "~"
        else:
            root_path = current_project.path

        self.asset_name_lineedit.clear()
        self.model_path_wgt.line_edit.clear()
        self.rig_path_wgt.line_edit.clear()
        self.file_system.setRootPath(root_path)
        self.file_tree.setRootIndex(self.file_system.index(root_path))

    @QtCore.Slot()
    def update_asset_completion(self):
        current_project = luna.workspace.Project.get()
        if not current_project:
            self.asset_name_lineedit.setCompleter(None)
            return
        project_meta = current_project.meta_data
        asset_list = project_meta.get(self.asset_type_cmbox.currentText() + "s", [])
        if not asset_list:
            self.asset_name_lineedit.setCompleter(None)
            return

        completer = QtWidgets.QCompleter(asset_list)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.asset_name_lineedit.setCompleter(completer)

    @QtCore.Slot()
    def open_asset_file(self, file_type, reference=False):
        if file_type == "model":
            file_path = self.model_path_wgt.line_edit.text()
        elif file_type == "rig":
            file_path = self.rig_path_wgt.line_edit.text()

        if not os.path.isfile(file_path):
            Logger.warning("Invalid file path: {0}".format(file_path))
            return

        if reference:
            pm.createReference(file_path)
        else:
            pm.openFile(file_path, f=1)

    @QtCore.Slot()
    def open_file(self, index):
        if self.file_system.isDir(index):
            return
        path = self.file_system.filePath(index)  # type: str
        path = os.path.normpath(path)
        if path.endswith(".ma") or path.endswith(".mb"):
            pm.openFile(path, f=1)
        else:
            if os.sys.platform == "win32":
                os.startfile(path)
            else:
                opener = "open" if os.sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, path])

    @QtCore.Slot()
    def reveal_in_explorer(self, index):
        path = self.file_system.filePath(index)  # type: str
        if os.path.isfile(path):
            path = os.path.dirname(path)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))

    @QtCore.Slot()
    def save_model_path(self):
        current_asset = luna.workspace.Asset.get()
        if not current_asset:
            return
        if self.model_path_wgt.line_edit.text() == current_asset.model_path:
            return
        current_asset.set_data("model", self.model_path_wgt.line_edit.text())
        Logger.info("Set asset model to {0}".format(self.model_path_wgt.line_edit.text()))

    @QtCore.Slot()
    def file_context_menu(self, point):
        context_menu = QtWidgets.QMenu("File menu", self)
        open_action = QtWidgets.QAction("Open", self)
        reveal_action = QtWidgets.QAction("Reveal in explorer", self)
        open_action.triggered.connect(lambda: self.open_file(self.file_tree.currentIndex()))
        reveal_action.triggered.connect(lambda: self.reveal_in_explorer(self.file_tree.currentIndex()))

        context_menu.addAction(open_action)
        context_menu.addAction(reveal_action)
        context_menu.exec_(self.file_tree.mapToGlobal(point))
