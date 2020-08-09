from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
import pymel.api as pma
import pymel.core as pm
from shiboken2 import getCppPointer
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from Luna import Logger


class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    WINDOW_TITLE = "Luna build manager"
    UI_NAME = "LunaBuildManager"
    UI_SCRIPT = "from Luna.tools import buildManager\nbuildManager.MainDialog()"
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
        self.create_actions()
        self.create_menu_bar()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_actions(self):
        self.documentation_action = QtWidgets.QAction("Documentation", self)
        self.documentation_action.setIcon(QtGui.QIcon(":help.png"))

    def create_menu_bar(self):
        # Help menu
        help_menu = QtWidgets.QMenu("Help")
        help_menu.addAction(self.documentation_action)
        # Menubar
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.addMenu(help_menu)

    def create_widgets(self):
        self.section_splitter = QtWidgets.QSplitter()

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setMenuBar(self.menuBar)
        self.main_layout.addWidget(self.section_splitter)

    def create_connections(self):
        pass


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
