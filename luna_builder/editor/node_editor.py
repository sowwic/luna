import imp
import json
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger
from luna.workspace import Asset
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.node_scene as node_scene
import luna_builder.editor.graphics_view as graphics_view
import luna_builder.editor.node_context_menus as context_menus
import luna_builder.editor.node_nodes_palette as node_nodes_palette

imp.reload(context_menus)
imp.reload(node_scene)
imp.reload(graphics_view)


class EditorSignals(QtCore.QObject):
    about_to_close = QtCore.Signal(QtWidgets.QWidget, QtCore.QEvent)


class NodeEditor(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.signals = EditorSignals()
        self.init_ui()
        self.scene.set_history_init_point()

    def init_ui(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(200, 500)
        self.create_widgets()
        self.create_actions()
        self.create_layouts()
        self.create_conections()
        self.update_title()

    def create_actions(self):
        self.addAction(node_nodes_palette.PopupNodesPalette.show_action(self, self.gr_view))

    def create_widgets(self):
        # Graphics scene
        self.scene = node_scene.Scene()

        # Graphics view
        self.gr_view = graphics_view.QLGraphicsView(self.scene.gr_scene, self)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.gr_view)

    def create_conections(self):
        self.scene.signals.file_name_changed.connect(self.update_title)
        self.scene.signals.modified.connect(self.update_title)
        self.scene.signals.item_drag_entered.connect(self.on_item_drag_enter)
        self.scene.signals.item_dropped.connect(self.on_item_drop)

    # ======== Properties ======== #
    @property
    def file_name(self):
        return self.scene.file_name

    @property
    def file_base_name(self):
        name = self.scene.file_base_name
        if not name:
            return 'Untitled'
        return name

    @property
    def user_friendly_title(self):
        filename = self.file_base_name
        if self.scene.has_been_modified:
            filename += '*'
        return filename

    # ======== Events ======== #
    def closeEvent(self, event):
        self.signals.about_to_close.emit(self, event)

    def contextMenuEvent(self, event):
        if self.gr_view.is_view_dragging:
            event.ignore()
            return

        try:
            item = self.scene.get_item_at(event.pos())
            if not item:
                self.handle_node_context_menu(event)
            if hasattr(item, 'node') or hasattr(item, 'socket') or not item:
                self.handle_node_context_menu(event)
            elif hasattr(item, 'edge'):
                self.handle_edge_context_menu(event)

            return super(NodeEditor, self).contextMenuEvent(event)
        except Exception:
            Logger.exception('ContextMenuEvent exception')

    # ======== Context menus ======== #

    def handle_node_context_menu(self, event):
        ctx_menu = context_menus.NodeContextMenu(self)
        ctx_menu.exec_(self.mapToGlobal(event.pos()))

    def handle_edge_context_menu(self, event):
        pass

    # ======== Drag & Drop ======== #

    def on_item_drag_enter(self, event):
        Logger.debug('On item drag enter')
        if event.mimeData().hasFormat(editor_conf.PALETTE_MIMETYPE) or event.mimeData().hasFormat(editor_conf.VARS_MIMETYPE):
            event.acceptProposedAction()
        else:
            Logger.warning('Unsupported item: {0}'.format(event.mimeData().formats()))
            event.setAccepted(False)

    def on_item_drop(self, event):
        Logger.debug('On item drop')
        if event.mimeData().hasFormat(editor_conf.PALETTE_MIMETYPE):
            self.handle_nodes_palette_drop(event)
        elif event.mimeData().hasFormat(editor_conf.VARS_MIMETYPE):
            self.handle_variable_drop(event)
        else:
            Logger.warning('Unsupported item format: {0}'.format(event.mimeData()))
            event.ignore()
            return

    # ======== Methods ======== #

    def handle_nodes_palette_drop(self, event):
        # Retrive data from droped item
        event_data = event.mimeData().data(editor_conf.PALETTE_MIMETYPE)
        data_stream = QtCore.QDataStream(event_data, QtCore.QIODevice.ReadOnly)
        pixmap = QtGui.QPixmap()
        data_stream >> pixmap
        node_id = data_stream.readInt32()
        json_data = json.loads(data_stream.readQString())  # type: dict
        # Position
        mouse_pos = event.pos()
        scene_pos = self.scene.view.mapToScene(mouse_pos)

        Logger.debug('''Dropped Item:
                        > NODE_ID: {node_id}
                        > DATA: {data}
                        > MOUSE POS: {mouse_pos}
                        > SCENE POS {scene_pos}'''.format(node_id=node_id, data=json_data, mouse_pos=mouse_pos, scene_pos=scene_pos))

        self.scene.spawn_node_from_data(node_id, json_data, scene_pos)

        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    def handle_variable_drop(self, event):
        event_data = event.mimeData().data(editor_conf.VARS_MIMETYPE)
        data_stream = QtCore.QDataStream(event_data, QtCore.QIODevice.ReadOnly)
        json_data = json.loads(data_stream.readQString())  # type: dict
        # Position
        mouse_pos = event.pos()
        scene_pos = self.scene.view.mapToScene(mouse_pos)
        Logger.debug('''Dropped Varible:
                        > DATA: {data}
                        > SCENE POS {scene_pos}'''.format(data=json_data, scene_pos=scene_pos))

        # Choose getter/setter
        var_name = json_data['var_name']
        get_set_menu = QtWidgets.QMenu(self)
        getter_action = QtWidgets.QAction('Get', get_set_menu)
        setter_action = QtWidgets.QAction('Set', get_set_menu)
        get_set_menu.addAction(getter_action)
        get_set_menu.addAction(setter_action)
        result_action = get_set_menu.exec_(self.mapToGlobal(event.pos()))
        if result_action is None:
            return
        # Spawn node
        self.scene.spawn_getset(var_name, scene_pos, setter=result_action == setter_action)
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    def update_title(self):
        self.setWindowTitle(self.user_friendly_title)

    def is_modified(self):
        return self.scene.has_been_modified

    def maybe_save(self):
        if not self.is_modified():
            return True

        res = QtWidgets.QMessageBox.warning(self, 'Warning: Build not saved',
                                            'Save changes to current build?',
                                            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
        if res == QtWidgets.QMessageBox.Save:
            return self.on_build_save()
        if res == QtWidgets.QMessageBox.Cancel:
            return False
        return True

    def on_build_new(self):
        if self.maybe_save():
            self.scene.clear()
            self.scene.file_name = None

    def on_build_open(self):
        if not Asset.get():
            Logger.warning('Asset is not set')
            return
        if not self.maybe_save():
            return

        rig_filter = "Rig Build (*.rig)"
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Open rig build scene", Asset.get().build, rig_filter)[0]
        if not file_path:
            return False
        self.scene.load_from_file(file_path)
        return True

    def on_build_save(self):
        if not Asset.get():
            Logger.warning('Asset is not set')
            return

        res = True
        if self.scene.file_name:
            self.scene.save_to_file(self.scene.file_name)
        else:
            res = self.on_build_save_as()
        return res

    def on_build_save_as(self):
        if not Asset.get():
            Logger.warning('Asset is not set')
            return

        rig_filter = "Rig Build (*.rig)"
        file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save build graph to file', Asset.get().new_build_path, rig_filter)[0]
        if not file_path:
            return False
        self.scene.save_to_file(file_path)
        return True
