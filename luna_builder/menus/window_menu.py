from PySide2 import QtWidgets
from luna import Logger


class WindowMenu(QtWidgets.QMenu):
    def __init__(self, main_window, parent=None):
        super(WindowMenu, self).__init__("&Window", parent)
        self.main_window = main_window

        self.setTearOffEnabled(True)
        self.create_actions()
        self.populate()
        self.create_connections()

    def create_actions(self):
        self.close_current_action = QtWidgets.QAction('Close', self)
        self.close_all_action = QtWidgets.QAction('Close All', self)
        self.tile_action = QtWidgets.QAction('Tile', self)
        self.next_wnd_action = QtWidgets.QAction('Next', self)
        self.previous_wnd_action = QtWidgets.QAction('Previous', self)

        self.next_wnd_action.setShortcut('Ctrl+Tab')
        self.previous_wnd_action.setShortcut('Ctrl+Shift+Backtab')

    def create_connections(self):
        self.aboutToShow.connect(self.update_actions_state)
        # Actions
        self.close_current_action.triggered.connect(self.main_window.mdi_area.closeActiveSubWindow)
        self.close_all_action.triggered.connect(self.main_window.mdi_area.closeAllSubWindows)
        self.tile_action.triggered.connect(self.main_window.mdi_area.tileSubWindows)
        self.next_wnd_action.triggered.connect(self.main_window.mdi_area.activateNextSubWindow)
        self.previous_wnd_action.triggered.connect(self.main_window.mdi_area.activatePreviousSubWindow)

    def populate(self):
        self.addAction(self.main_window.nodes_palette_dock.toggleViewAction())
        self.addAction(self.main_window.vars_dock.toggleViewAction())
        self.addAction(self.main_window.workspace_dock.toggleViewAction())
        self.addAction(self.main_window.attrib_editor_dock.toggleViewAction())

        self.addSeparator()
        self.addAction(self.close_current_action)
        self.addAction(self.close_all_action)
        self.addSeparator()
        self.addAction(self.tile_action)
        self.addSeparator()
        self.addAction(self.next_wnd_action)
        self.addAction(self.previous_wnd_action)

    def update_actions_state(self):
        has_mdi_child = self.main_window.current_editor is not None
        self.close_current_action.setEnabled(has_mdi_child)
        self.close_all_action.setEnabled(has_mdi_child)
        self.tile_action.setEnabled(has_mdi_child)
        self.next_wnd_action.setEnabled(has_mdi_child)
        self.previous_wnd_action.setEnabled(has_mdi_child)
