from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
import pymel.api as pma
import pymel.core as pm
from shiboken2 import getCppPointer
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from Luna import Logger


class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    WINDOW_TITLE = "Luna configuaration"
    UI_NAME = "LunaConfigManager"
    UI_SCRIPT = "from Luna.tools import configManager\nconfigManager.MainDialog()"
    UI_INSTANCE = None
    MINIMUM_SIZE = [400, 500]

    DEFAULT_SETTINGS = {}

    @classmethod
    def display(cls):
        if not cls.UI_INSTANCE:
            cls.UI_INSTANCE = MainDialog()

        if cls.UI_INSTANCE.isHidden():
            cls.UI_INSTANCE.show(dockable=1, uiScript=cls.UI_SCRIPT)
        else:
            cls.UI_INSTANCE.raise_()
            cls.UI_INSTANCE.activateWindow()

    def __init__(self):
        super(MainDialog, self).__init__()

        # Window adjustments
        self.__class__.UI_INSTANCE = self
        self.setObjectName(self.__class__.UI_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(*self.MINIMUM_SIZE)
        self.setMaximumHeight(600)

        # Workspace control
        self.workspaceControlName = "{0}WorkspaceControl".format(self.UI_NAME)
        if pm.workspaceControl(self.workspaceControlName, q=1, ex=1):
            workspaceControlPtr = long(pma.MQtUtil.findControl(self.workspaceControlName))
            widgetPtr = long(getCppPointer(self)[0])
            pma.MQtUtil.addWidgetToMayaLayout(widgetPtr, workspaceControlPtr)

        # UI setup
        self.configs = self.load_configs()
        self.create_actions()
        self.create_menu_bar()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_actions(self):
        self.reset_configs_action = QtWidgets.QAction("Restore default config", self)
        self.documentation_action = QtWidgets.QAction("Documentation", self)
        self.documentation_action.setIcon(QtGui.QIcon(":help.png"))

    def create_menu_bar(self):
        # Edit menu
        edit_menu = QtWidgets.QMenu("&Edit")
        edit_menu.addAction(self.reset_configs_action)
        # Help menu
        help_menu = QtWidgets.QMenu("Help")
        help_menu.addAction(self.documentation_action)
        # Menubar
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.addMenu(edit_menu)
        self.menuBar.addMenu(help_menu)

    def create_widgets(self):
        self.config_splitter = QtWidgets.QSplitter()
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.setMinimumWidth(90)
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(90)

    def create_layouts(self):
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setMenuBar(self.menuBar)
        self.main_layout.addWidget(self.config_splitter)
        self.main_layout.addLayout(self.buttons_layout)

    def create_connections(self):
        self.save_button.clicked.connect(self.save_configs)
        self.cancel_button.clicked.connect(self.hide)

    def load_configs(self):
        Logger.debug("TODO: load_configs")

    def save_configs(self):
        Logger.debug("TODO: save_configs")
        self.hide()

    def update_configs(self):
        Logger.debug("TODO: update_configs")


if __name__ == "__main__":
    try:
        if testTool and testTool.parent():  # noqa: F821
            workspaceControlName = testTool.parent().objectName()  # noqa: F821

            if pm.window(workspaceControlName, ex=1, q=1):
                pm.deleteUI(workspaceControlName)
    except Exception:
        pass

    testTool = MainDialog()
    testTool.show(dockable=1, uiScript=testTool.UI_SCRIPT)
