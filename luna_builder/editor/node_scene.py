import imp
import json
import os
import timeit
import uuid
from collections import OrderedDict
from PySide2 import QtCore
from PySide2 import QtWidgets

from luna import Logger
import luna.utils.fileFn as fileFn
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.node_node as node_node
import luna_builder.editor.node_edge as node_edge
import luna_builder.editor.graphics_scene as graphics_scene
import luna_builder.editor.node_serializable as node_serializable
import luna_builder.editor.node_scene_history as scene_history
import luna_builder.editor.node_scene_clipboard as scene_clipboard
import luna_builder.editor.node_scene_vars as node_scene_vars
import luna_builder.editor.graph_executor as graph_executor
# imp.reload(node_scene_vars)
imp.reload(scene_history)
imp.reload(scene_clipboard)
imp.reload(graphics_scene)


class SceneSignals(QtCore.QObject):
    modified = QtCore.Signal()
    file_name_changed = QtCore.Signal(str)
    item_selected = QtCore.Signal()
    items_deselected = QtCore.Signal()
    item_drag_entered = QtCore.Signal(QtCore.QEvent)
    item_dropped = QtCore.Signal(QtCore.QEvent)
    file_load_finished = QtCore.Signal()


class Scene(node_serializable.Serializable):

    def __init__(self):
        super(Scene, self).__init__()
        self.signals = SceneSignals()
        self._file_name = None
        self._has_been_modified = False
        self._items_are_being_deleted = False
        self._last_selected_items = []

        self.nodes = []
        self.edges = []
        self.is_executing = False
        self.executor = self.executor = graph_executor.GraphExecutor(self)
        self.vars = node_scene_vars.SceneVars(self)
        self.gr_scene = None  # type: graphics_scene.QLGraphicsScene

        self.scene_width = 64000
        self.scene_height = 64000
        self._edge_type = node_edge.Edge.Type.BEZIER

        self.init_ui()
        self.history = scene_history.SceneHistory(self)
        self.clipboard = scene_clipboard.SceneClipboard(self)
        self.create_connections()

    def init_ui(self):
        self.gr_scene = graphics_scene.QLGraphicsScene(self)
        self.gr_scene.set_scene_size(self.scene_width, self.scene_height)

    def create_connections(self):
        self.gr_scene.selectionChanged.connect(self.on_selection_change)

    @ property
    def edge_type(self):
        return self._edge_type

    @ edge_type.setter
    def edge_type(self, value):
        # Get edge type
        fallback_type = node_edge.Edge.Type.BEZIER
        if isinstance(value, int):
            try:
                value = list(node_edge.Edge.Type)[value]
            except IndexError:
                value = fallback_type
        elif isinstance(value, node_edge.Edge.Type):
            pass
        else:
            try:
                value = node_edge.Edge.Type[str(value)]
            except Exception:
                Logger.error('Scene: Invalid edge type value: {0}'.format(value))
                value = fallback_type

        if self._edge_type == value:
            return
        # Do updates
        self._edge_type = value
        self.update_edge_types()

    @ property
    def view(self):
        return self.gr_scene.views()[0]

    @ property
    def has_been_modified(self):
        return self._has_been_modified

    @ has_been_modified.setter
    def has_been_modified(self, value):
        self._has_been_modified = value
        self.signals.modified.emit()

    @ property
    def file_name(self):
        return self._file_name

    @ file_name.setter
    def file_name(self, value):
        self._file_name = value
        self.signals.file_name_changed.emit(self._file_name)

    @ property
    def file_base_name(self):
        if not self.file_name:
            return None
        return os.path.basename(self.file_name)

    @ property
    def selected_items(self):
        return self.gr_scene.selectedItems()

    @ property
    def selected_nodes(self):
        return [node for node in self.nodes if node.gr_node.isSelected()]

    @ property
    def selected_edges(self):
        return [edge for edge in self.edges if edge.gr_edge.isSelected()]

    @ property
    def last_selected_items(self):
        return self._last_selected_items

    def set_history_init_point(self):
        Logger.debug('Store initial scene history (Size: {0})'.format(self.history.size))
        self.history.store_history(self.history.SCENE_INIT_DESC)

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_node(self, node):
        self.nodes.remove(node)

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def list_node_ids(self):
        return [node.uid for node in self.nodes]

    def list_edges_ids(self):
        return [node.uid for node in self.edges]

    def get_item_at(self, position):
        return self.view.itemAt(position)

    def clear(self):
        while(self.nodes):
            self.nodes[0].remove(silent=True)
        self.has_been_modified = False

    def update_edge_types(self):
        for edge in self.edges:
            edge.update_edge_graphics_type()

    # ====== Selection ====== #
    def on_selection_change(self):
        # Ignore selection update if rubberband dragging, item deletion is in progress
        if any([self.view.rubberband_dragging_rect,
                self._items_are_being_deleted]):
            return

        current_selection = self.gr_scene.selectedItems()
        if current_selection == self.last_selected_items:
            return

        # No current selection and existing previous selection (To avoid resetting selection after cut operation)
        if not current_selection:
            self.history.store_history('Deselected everything', set_modified=False)
            self.signals.items_deselected.emit()
        else:
            self.history.store_history('Selection changed', set_modified=False)
            self.signals.item_selected.emit()
        self._last_selected_items = current_selection

    def rename_selected_node(self):
        sel = self.selected_nodes
        if not sel:
            Logger.warning('Select a node to rename.')
            return
        sel = sel[-1]
        sel.edit_title()

    # ====== Cut / Copy / Paste / Delete ====== #
    def copy_selected(self):
        if not self.selected_nodes:
            Logger.warning('No nodes selected to copy')
            return

        try:
            data = self.clipboard.serialize_selected(delete=False)
            str_data = json.dumps(data, indent=4)
            QtWidgets.QApplication.clipboard().setText(str_data)
        except Exception:
            Logger.exception('Copy exception')

    def cut_selected(self):
        if not self.selected_nodes:
            Logger.warning('No nodes selected to copy')
            return

        try:
            data = self.clipboard.serialize_selected(delete=True)
            str_data = json.dumps(data, indent=4)
            QtWidgets.QApplication.clipboard().setText(str_data)
            self._last_selected_items = []
        except Exception:
            Logger.exception('Cut exception')

    def paste_from_clipboard(self):
        raw_data = QtWidgets.QApplication.clipboard().text()
        try:
            data = json.loads(raw_data)  # type: dict
        except ValueError:
            Logger.error('Invalid json paste data')
            return

        if 'nodes' not in data.keys():
            Logger.warning('Clipboard JSON does not contain any nodes')
            return

        self.clipboard.deserialize_from_clip(data)

    def delete_selected(self, store_history=True):
        self._items_are_being_deleted = True
        try:
            for node in self.selected_nodes:
                node.remove()
            for edge in self.selected_edges:
                edge.remove()
        except Exception:
            Logger.exception('Failed to delete selected items')
        self._items_are_being_deleted = False
        if store_history:
            self.history.store_history('Item deleted', set_modified=True)
        self.signals.items_deselected.emit()

    # ====== File ====== #

    def save_to_file(self, file_path):
        try:
            fileFn.write_json(file_path, data=self.serialize(), sort_keys=False)
            Logger.info('Saved build {0}'.format(file_path))
            self.file_name = file_path
            self.has_been_modified = False
            self.signals.modified.emit()
        except Exception:
            Logger.exception('Failed to save build')

    def load_from_file(self, file_path):
        try:
            self.clear()
            start_time = timeit.default_timer()
            data = fileFn.load_json(file_path, object_pairs_hook=OrderedDict)
            self.deserialize(data)
            Logger.info("Rig build loaded in {0:.2f}s".format(timeit.default_timer() - start_time))
            self.history.clear()
            self.executor.reset_stepped_execution()
            self.file_name = file_path
            self.has_been_modified = False
            self.set_history_init_point()
            self.signals.file_load_finished.emit()
        except Exception:
            Logger.exception('Failed to load rig build file')

    # Creation

    @ classmethod
    def get_class_from_node_data(cls, node_data):
        node_id = node_data.get('node_id')
        if not node_id:
            return node_node.Node
        else:
            return editor_conf.get_node_class_from_id(node_id)

    def spawn_node_from_data(self, node_id, json_data, position):
        try:
            new_node = editor_conf.get_node_class_from_id(node_id)(self)
            if node_id == editor_conf.FUNC_NODE_ID:
                new_node.title = json_data.get('title')
                new_node.func_signature = json_data.get('func_signature', '')

            new_node.set_position(position.x(), position.y())
            self.history.store_history('Created Node {0}'.format(new_node.as_str(name_only=True)))
            return new_node
        except Exception:
            Logger.exception('Failed to instance node')

    def spawn_getset(self, var_name, scene_pos, setter=False):
        node_id = editor_conf.SET_NODE_ID if setter else editor_conf.GET_NODE_ID
        try:
            node = editor_conf.get_node_class_from_id(node_id)(self)
            node.set_var_name(var_name, init_sockets=True)
            node.set_position(scene_pos.x(), scene_pos.y())
            self.history.store_history('Created Node {0}'.format(node.as_str(name_only=True)))
            return node
        except Exception:
            Logger.exception('Failed to instance getter node')

    def regenerate_uuids(self):
        obj_count = 1
        self.uid = str(uuid.uuid4())
        for node in self.nodes:
            node.uid = str(uuid.uuid4())
            obj_count += 1
            for socket in node.inputs + node.outputs:
                socket.uid = str(uuid.uuid4())
                obj_count += 1
        for edge in self.edges:
            edge.uid = str(uuid.uuid4())
            obj_count += 1
        Logger.info('Generated new UUIDs for {0} objects'.format(obj_count))

    def serialize(self):
        nodes, edges = [], []
        for n in self.nodes:
            nodes.append(n.serialize())

        for e in self.edges:
            if not e.start_socket or not e.end_socket:
                continue
            edges.append(e.serialize())

        return OrderedDict([
            ('id', self.uid),
            ('vars', self.vars.serialize()),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges),
            ('edge_type', self.edge_type.name)
        ])

    def deserialize(self, data, hashmap=None, restore_id=True):
        if hashmap is None:
            hashmap = {}

        if restore_id:
            self.uid = data['id']
        self.vars.deserialize(data.get('vars', OrderedDict()))

        # Deserialize nodes
        all_nodes = self.nodes[:]
        for node_data in data['nodes']:
            found = False
            for node in all_nodes:
                if node.uid == node_data['id']:
                    found = node
                    break

            if not found:
                new_node = self.get_class_from_node_data(node_data)(self)
                new_node.deserialize(node_data, hashmap, restore_id=restore_id)
            else:
                found.deserialize(node_data, hashmap, restore_id=restore_id)
                all_nodes.remove(found)

        while all_nodes:
            node = all_nodes.pop()
            node.remove()

        # Deserialize edges
        all_edges = self.edges[:]

        for edge_data in data['edges']:
            found = False
            for edge in all_edges:
                if edge.uid == edge_data['id']:
                    found = edge
                    break
            if not found:
                new_edge = node_edge.Edge(self)
                new_edge.deserialize(edge_data, hashmap, restore_id)
            else:
                found.deserialize(edge_data, hashmap, restore_id)
                all_edges.remove(found)

        while all_edges:
            edge = all_edges.pop()
            try:
                self.edges.index(edge)
            except ValueError:
                continue
            edge.remove()

        # Set edge type
        self.edge_type = data.get('edge_type', node_edge.Edge.Type.BEZIER)

        return True
