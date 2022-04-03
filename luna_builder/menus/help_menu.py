from PySide2 import QtWidgets
import luna.utils.pysideFn as pysideFn
import luna_builder.editor.editor_conf as editor_conf


class HelpMenu(QtWidgets.QMenu):
    def __init__(self, main_window, parent=None):
        super(HelpMenu, self).__init__("Help", parent)
        self.main_window = main_window
        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        pass

    def create_actions(self):
        self.reload_editor_plugins_action = QtWidgets.QAction('Reload editor plugins', self)
        self.docs_action = QtWidgets.QAction(pysideFn.get_QIcon("help.png", maya_icon=True), "Documentation", self)

    def create_connections(self):
        self.reload_editor_plugins_action.triggered.connect(editor_conf.load_plugins)
        self.reload_editor_plugins_action.triggered.connect(self.main_window.nodes_palette.update_node_tree)

    def populate(self):
        self.addAction(self.reload_editor_plugins_action)
        self.addAction(self.docs_action)

    def update_actions_state(self):
        pass
