from PySide2 import QtWidgets


class NodeContextMenu(QtWidgets.QMenu):
    def __init__(self, editor):
        super(NodeContextMenu, self).__init__("Node", editor)
        self.scene = editor.scene

        self.create_actions()
        self.populate()
        self.create_connections()

    def create_actions(self):
        self.copy_action = QtWidgets.QAction("&Copy", self)
        self.cut_action = QtWidgets.QAction("&Cut", self)
        self.paste_action = QtWidgets.QAction("&Paste", self)
        self.delete_action = QtWidgets.QAction("&Delete", self)

    def create_connections(self):
        self.copy_action.triggered.connect(self.on_copy)
        self.cut_action.triggered.connect(self.on_cut)
        self.paste_action.triggered.connect(self.on_paste)
        self.delete_action.triggered.connect(self.on_delete)

    def populate(self):
        self.addAction(self.copy_action)
        self.addAction(self.cut_action)
        self.addAction(self.paste_action)
        self.addSeparator()
        self.addAction(self.delete_action)

    def on_copy(self):
        if self.scene:
            self.scene.copy_selected()

    def on_cut(self):
        if self.scene:
            self.scene.cut_selected()

    def on_paste(self):
        if self.scene:
            self.scene.paste_from_clipboard()

    def on_delete(self):
        if self.scene:
            self.scene.delete_selected()
