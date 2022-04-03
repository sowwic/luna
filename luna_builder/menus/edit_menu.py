import json
from PySide2 import QtWidgets
from luna import Logger


class EditMenu(QtWidgets.QMenu):
    def __init__(self, main_window, parent=None):
        super(EditMenu, self).__init__("&Edit", parent)
        self.main_window = main_window

        self.setTearOffEnabled(True)
        self.create_actions()
        self.populate()
        self.create_connections()

    @property
    def node_scene(self):
        editor = self.main_window.current_editor
        if not editor:
            return None
        return editor.scene

    @property
    def gr_view(self):
        editor = self.main_window.current_editor
        if not editor:
            return None
        return editor.gr_view

    def create_actions(self):
        self.rename_selected_node_action = QtWidgets.QAction('Rename selected node', self)
        self.regenerate_uuids_action = QtWidgets.QAction('Regenerate UUIDs', self)
        self.undo_action = QtWidgets.QAction("&Undo", self)
        self.redo_action = QtWidgets.QAction("&Redo", self)
        self.copy_action = QtWidgets.QAction("&Copy", self)
        self.cut_action = QtWidgets.QAction("&Cut", self)
        self.paste_action = QtWidgets.QAction("&Paste", self)
        self.delete_action = QtWidgets.QAction("&Delete", self)

        # self.addAction(self.rename_selected_node_action)

        self.rename_selected_node_action.setShortcut('F2')
        self.undo_action.setShortcut('Ctrl+Z')
        self.redo_action.setShortcut('Ctrl+Y')
        self.copy_action.setShortcut('Ctrl+C')
        self.cut_action.setShortcut('Ctrl+X')
        self.paste_action.setShortcut('Ctrl+V')
        self.delete_action.setShortcut('Del')

    def create_connections(self):
        self.main_window.mdi_area.subWindowActivated.connect(self.update_actions_state)
        self.aboutToShow.connect(self.update_actions_state)
        # Actions
        self.rename_selected_node_action.triggered.connect(self.on_rename_selected_node)
        self.regenerate_uuids_action.triggered.connect(self.on_regenerate_uuids)
        self.undo_action.triggered.connect(self.on_undo)
        self.redo_action.triggered.connect(self.on_redo)
        self.copy_action.triggered.connect(self.on_copy)
        self.cut_action.triggered.connect(self.on_cut)
        self.paste_action.triggered.connect(self.on_paste)
        self.delete_action.triggered.connect(self.on_delete)

    def populate(self):
        self.addAction(self.rename_selected_node_action)
        # self.addAction(self.regenerate_uuids_action)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addSeparator()
        self.addAction(self.copy_action)
        self.addAction(self.cut_action)
        self.addAction(self.paste_action)
        self.addSeparator()
        self.addAction(self.delete_action)

    def update_actions_state(self):
        is_scene_set = self.node_scene is not None
        self.rename_selected_node_action.setEnabled(is_scene_set)
        self.undo_action.setEnabled(is_scene_set)
        self.redo_action.setEnabled(is_scene_set)
        self.copy_action.setEnabled(is_scene_set)
        self.cut_action.setEnabled(is_scene_set)
        self.paste_action.setEnabled(is_scene_set)
        self.delete_action.setEnabled(is_scene_set)

    def on_rename_selected_node(self):
        if self.node_scene is not None:
            try:
                self.node_scene.rename_selected_node()
            except Exception:
                Logger.exception('Node rename exception')

    def on_undo(self):
        if self.node_scene is not None:
            try:
                self.node_scene.history.undo()
                self.main_window.refresh_variables()
            except Exception:
                Logger.exception('Undo exception')
                raise

    def on_redo(self):
        if self.node_scene is not None:
            try:
                self.node_scene.history.redo()
                self.main_window.refresh_variables()
            except Exception:
                Logger.exception('Redo exception')
                raise

    def on_copy(self):
        if self.node_scene:
            self.node_scene.copy_selected()

    def on_cut(self):
        if self.node_scene:
            self.node_scene.cut_selected()

    def on_paste(self):
        if self.node_scene:
            self.node_scene.paste_from_clipboard()

    def on_delete(self):
        if self.node_scene:
            self.node_scene.delete_selected()

    def on_regenerate_uuids(self):
        if self.node_scene:
            self.node_scene.regenerate_uuids()
