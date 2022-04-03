
import imp
from PySide2 import QtCore
from PySide2 import QtWidgets

from luna import Logger
from luna import __version__
from luna.utils import pysideFn

import luna_builder.editor.workspace_widget as workspace_widget
import luna_builder.editor.attributes_editor as attributes_editor

import luna_builder.menus as menus
import luna_builder.editor.node_editor as node_editor
import luna_builder.editor.node_nodes_palette as node_nodes_palette
import luna_builder.editor.node_scene_vars as node_scene_vars

imp.reload(node_scene_vars)
imp.reload(node_editor)
imp.reload(attributes_editor)
imp.reload(workspace_widget)
imp.reload(node_nodes_palette)


class BuilderMainWindow(QtWidgets.QMainWindow):
    WINDOW_TITLE = "Luna builder v" + __version__
    DOCKED_TITLE = "Luna builder"
    INSTANCE = None  # type: BuilderMainWindow
    GEOMETRY = None
    MINIMUM_SIZE = [400, 500]

    @classmethod
    def display(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = cls()

        if cls.INSTANCE.isHidden():
            cls.INSTANCE.show()
        else:
            cls.INSTANCE.raise_()
            cls.INSTANCE.activateWindow()

        if cls.GEOMETRY:
            cls.INSTANCE.restoreGeometry(cls.GEOMETRY)
        else:
            pysideFn.move_window_to_center(cls.INSTANCE)

    @classmethod
    def close_and_delete(cls):
        if not cls.INSTANCE:
            return
        cls.INSTANCE.close()
        cls.INSTANCE.deleteLater()
        cls.INSTANCE = None

    def closeEvent(self, event):
        BuilderMainWindow.GEOMETRY = self.saveGeometry()
        super(BuilderMainWindow, self).closeEvent(event)

    def __init__(self, parent=pysideFn.maya_main_window()):
        super(BuilderMainWindow, self).__init__(parent)

        # Window adjustments
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowIcon(pysideFn.get_QIcon("builder.svg"))
        self.setMinimumSize(*self.MINIMUM_SIZE)
        self.setProperty("saveWindowPref", True)

        # UI setup
        self.create_actions()
        self.create_widgets()
        self.create_menu_bar()
        self.create_layouts()
        self.create_connections()

    def create_actions(self):
        pass

    def create_menu_bar(self):
        self.menu_bar = QtWidgets.QMenuBar()
        self.setMenuBar(self.menu_bar)
        # Corner button
        self.update_button = QtWidgets.QPushButton()
        self.update_button.setFlat(True)
        self.update_button.setIcon(pysideFn.get_QIcon("refresh.png"))
        self.menu_bar.setCornerWidget(self.update_button, QtCore.Qt.TopRightCorner)

        # Menus
        self.file_menu = menus.FileMenu(self)
        self.edit_menu = menus.EditMenu(self)
        self.graph_menu = menus.GraphMenu(self)
        self.window_menu = menus.WindowMenu(self)
        self.controls_menu = menus.ControlsMenu()
        self.joints_menu = menus.JointsMenu()
        self.skin_menu = menus.SkinMenu()
        self.deformers_menu = menus.DeformersMenu()
        self.rig_menu = menus.RigMenu()
        self.help_menu = menus.HelpMenu(self)

        # Populate menu bar
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.edit_menu)
        self.menu_bar.addMenu(self.graph_menu)
        self.menu_bar.addMenu(self.window_menu)
        self.menu_bar.addMenu(self.controls_menu)
        self.menu_bar.addMenu(self.joints_menu)
        self.menu_bar.addMenu(self.skin_menu)
        self.menu_bar.addMenu(self.deformers_menu)
        self.menu_bar.addMenu(self.rig_menu)
        self.menu_bar.addMenu(self.help_menu)

    def create_widgets(self):
        # Right tabs
        self.workspace_wgt = workspace_widget.WorkspaceWidget()
        self.attrib_editor = attributes_editor.AttributesEditor(self)

        # Nodes palette, vars widget
        self.nodes_palette = node_nodes_palette.NodesPalette()
        self.vars_widget = node_scene_vars.SceneVarsWidget(self)

        # Mdis
        self.mdi_area = QtWidgets.QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.mdi_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setViewMode(QtWidgets.QMdiArea.TabbedView)
        self.mdi_area.setDocumentMode(True)
        self.mdi_area.setTabsClosable(True)
        self.mdi_area.setTabsMovable(True)

        # Dock Widgets
        self.setTabPosition(QtCore.Qt.RightDockWidgetArea, QtWidgets.QTabWidget.East)
        self.setTabPosition(QtCore.Qt.LeftDockWidgetArea, QtWidgets.QTabWidget.North)
        # Workspace
        self.workspace_dock = QtWidgets.QDockWidget(self.workspace_wgt.label)
        self.workspace_dock.setWidget(self.workspace_wgt)
        self.workspace_dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        # Attrib editor
        self.attrib_editor_dock = QtWidgets.QDockWidget('Attributes')
        self.attrib_editor_dock.setWidget(self.attrib_editor)
        self.attrib_editor_dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        # Nodes palette
        self.nodes_palette_dock = QtWidgets.QDockWidget('Nodes Palette')
        self.nodes_palette_dock.setWidget(self.nodes_palette)
        self.nodes_palette_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        # Variables
        self.vars_dock = QtWidgets.QDockWidget('Variables')
        self.vars_dock.setWidget(self.vars_widget)
        self.vars_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)

        # Add docks right
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.workspace_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.attrib_editor_dock)
        self.tabifyDockWidget(self.workspace_dock, self.attrib_editor_dock)
        self.workspace_dock.raise_()
        # Add docks left
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.nodes_palette_dock)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.vars_dock)

    def create_layouts(self):
        self.hor_layout = QtWidgets.QHBoxLayout()
        self.hor_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def create_connections(self):
        # Other
        self.update_button.clicked.connect(self.workspace_wgt.update_data)
        self.update_button.clicked.connect(self.nodes_palette.update_node_tree)
        self.mdi_area.subWindowActivated.connect(self.update_title)
        self.mdi_area.subWindowActivated.connect(self.vars_widget.update_var_list)
        self.vars_widget.var_list.itemClicked.connect(self.attrib_editor.update_current_var_widget)

    @property
    def current_editor(self):
        if not self.current_window:
            return None
        editor = self.current_window.widget()  # type: node_editor.NodeEditor
        return editor

    @property
    def current_window(self):
        sub_wnd = self.mdi_area.currentSubWindow()  # type: QtWidgets.QMdiSubWindow
        return sub_wnd

    def create_mdi_child(self):
        new_editor = node_editor.NodeEditor()
        sub_wnd = self.mdi_area.addSubWindow(new_editor)  # type: QtWidgets.QMdiSubWindow
        # Signal connections
        new_editor.scene.signals.file_name_changed.connect(self.update_title)
        new_editor.scene.signals.modified.connect(self.update_title)
        new_editor.scene.signals.item_selected.connect(
            self.attrib_editor.update_current_node_widget)
        new_editor.scene.signals.items_deselected.connect(self.attrib_editor.clear)
        new_editor.signals.about_to_close.connect(self.on_sub_window_close)
        new_editor.scene.signals.file_load_finished.connect(self.vars_widget.update_var_list)
        return sub_wnd

    def find_mdi_child(self, file_name):
        for window in self.mdi_area.subWindowList():
            if window.widget().file_name == file_name:
                return window
        return None

    def set_active_sub_window(self, window):
        if window:
            self.mdi_area.setActiveSubWindow(window)

    def refresh_variables(self):
        self.vars_widget.update_var_list()

    def update_title(self):
        if not self.current_editor:
            self.setWindowTitle(self.WINDOW_TITLE)
            return

        friendly_title = self.current_editor.user_friendly_title
        self.setWindowTitle('{0} - {1}'.format(self.WINDOW_TITLE, friendly_title))

    def on_sub_window_close(self, widget, event):
        existing = self.find_mdi_child(widget.file_name)
        self.mdi_area.setActiveSubWindow(existing)

        if self.current_editor.maybe_save():
            event.accept()
            self.attrib_editor.clear()
        else:
            event.ignore()

    def on_build_open(self):
        sub_wnd = self.current_window if self.current_window else self.create_mdi_child()
        sub_wnd.widget().on_build_open()

    def on_build_open_tabbed(self):
        sub_wnd = self.create_mdi_child()
        res = sub_wnd.widget().on_build_open()
        if not res:
            self.mdi_area.removeSubWindow(sub_wnd)

    def on_build_new(self):
        try:
            sub_wnd = self.create_mdi_child()
            sub_wnd.show()
        except Exception:
            Logger.exception('Failed to create new build')

    def on_build_save(self):
        if self.current_editor:
            self.current_editor.on_build_save()

    def on_build_save_as(self):
        if self.current_editor:
            self.current_editor.on_build_save_as()


if __name__ == "__main__":
    BuilderMainWindow.INSTANCE = None
    BuilderMainWindow.display()
