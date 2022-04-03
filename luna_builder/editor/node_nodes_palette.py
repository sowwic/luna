import os
import json
import re
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger
import luna.static.directories as directories
import luna_builder.editor.node_edge as node_edge
import luna_builder.editor.editor_conf as editor_conf


class NodesPalette(QtWidgets.QWidget):
    def __init__(self, parent=None, icon_size=32, data_type_filter=None, functions_first=False):
        super(NodesPalette, self).__init__(parent)

        self.icon_size = QtCore.QSize(icon_size, icon_size)
        self.data_type_filter = data_type_filter
        self._functions_first = functions_first

        self.setMinimumWidth(190)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.update_node_tree()

    @property
    def functions_first(self):
        return self._functions_first

    @functions_first.setter
    def functions_first(self, state):
        self._functions_first = state
        self.update_node_tree()

    def create_widgets(self):
        self.search_line = QtWidgets.QLineEdit()
        self.search_line.setPlaceholderText('Search')
        self.nodes_tree = QLDragTreeWidget(self)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.search_line)
        self.main_layout.addWidget(self.nodes_tree)

    def create_connections(self):
        self.search_line.textChanged.connect(lambda text: self.nodes_tree.populate(search_filter=text))

    def update_node_tree(self):
        self.nodes_tree.populate()


class QLDragTreeWidget(QtWidgets.QTreeWidget):

    PIXMAP_ROLE = QtCore.Qt.UserRole
    NODE_ID_ROLE = QtCore.Qt.UserRole + 1
    JSON_DATA_ROLE = QtCore.Qt.UserRole + 2

    def __init__(self, nodes_palette, parent=None):
        super(QLDragTreeWidget, self).__init__(parent)
        self.nodes_palette = nodes_palette

        self.setIconSize(self.nodes_palette.icon_size)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.setHeaderHidden(True)

    def add_node_item(self, node_id, label_text, func_signature='', category='Undefiend', icon_name=None, expanded=True):
        if not icon_name:
            icon_name = 'func.png'
        icon_path = os.path.join(directories.ICONS_PATH, icon_name)
        pixmap = QtGui.QPixmap(icon_path)

        # Find parent
        category_path = category.split('/')
        parent_item = self
        for category_name in category_path:
            parent_item = self.get_category(category_name, parent=parent_item, expanded=expanded)

        # Setup item
        item = QtWidgets.QTreeWidgetItem()
        parent_item.addChild(item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
        item.setText(0, label_text)
        item.setIcon(0, QtGui.QIcon(pixmap))
        item.setSizeHint(0, self.nodes_palette.icon_size)
        # Setup item
        item.setData(0, QLDragTreeWidget.PIXMAP_ROLE, pixmap)
        item.setData(0, QLDragTreeWidget.NODE_ID_ROLE, node_id)
        json_data = {
            'title': item.text(0),
            'func_signature': func_signature
        }

        item.setData(0, QLDragTreeWidget.JSON_DATA_ROLE, json_data)
        return item

    def add_category(self, name, expanded=True, parent=None):
        if not parent:
            parent = self
        category_item = QtWidgets.QTreeWidgetItem(parent)
        category_item.setFlags(QtCore.Qt.ItemIsEnabled)
        category_item.setText(0, name)
        category_item.setExpanded(expanded)
        return category_item

    def get_category(self, name, expanded=True, parent=None):
        found_items = self.findItems(name, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
        if parent is not self:
            found_items = [item for item in found_items if item.parent() is parent]
        item = found_items[0] if found_items else self.add_category(name, expanded=expanded, parent=parent)
        return item

    def startDrag(self, event):
        Logger.debug('Palette::startDrag')
        try:
            item = self.currentItem()  # type: QtWidgets.QTreeWidgetItem
            node_id = item.data(0, QLDragTreeWidget.NODE_ID_ROLE)
            pixmap = QtGui.QPixmap(item.data(0, QLDragTreeWidget.PIXMAP_ROLE))

            # Pack data to json
            json_data = item.data(0, QLDragTreeWidget.JSON_DATA_ROLE)

            # Pack data to data stream
            item_data = QtCore.QByteArray()
            data_stream = QtCore.QDataStream(item_data, QtCore.QIODevice.WriteOnly)
            data_stream << pixmap
            data_stream.writeInt32(node_id)
            data_stream.writeQString(json.dumps(json_data))

            # Create mime data
            mime_data = QtCore.QMimeData()
            mime_data.setData(editor_conf.PALETTE_MIMETYPE, item_data)

            # Create drag
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2))
            drag.setPixmap(pixmap)

            Logger.debug('Dragging item <{0}>, {1}'.format(node_id, item))
            drag.exec_(QtCore.Qt.MoveAction)

        except Exception:
            Logger.exception('Palette drag exception')

    def populate(self, search_filter=''):
        self.clear()
        if self.nodes_palette.functions_first:
            self.add_registered_functions(search_filter=search_filter)
            self.add_registered_nodes(search_filter=search_filter)
        else:
            self.add_registered_nodes(search_filter=search_filter)
            self.add_registered_functions(search_filter=search_filter)

    def add_registered_nodes(self, search_filter=''):
        keys = list(editor_conf.NODE_REGISTER.keys())
        keys.sort()
        for node_id in keys:
            node_class = editor_conf.NODE_REGISTER[node_id]
            if node_class.CATEGORY == editor_conf.INTERNAL_CATEGORY:
                continue
            palette_label = node_class.PALETTE_LABEL if hasattr(node_class, 'PALETTE_LABEL') else node_class.DEFAULT_TITLE
            filter_matched = bool(search_filter) and (re.search(search_filter, palette_label, re.IGNORECASE)
                                                      is not None or re.search(search_filter, node_class.CATEGORY, re.IGNORECASE) is not None)
            # Filter
            if search_filter and not filter_matched:
                continue
            self.add_node_item(node_id, palette_label, category=node_class.CATEGORY, icon_name=node_class.ICON)

    def add_registered_functions(self, search_filter=''):
        keys = list(editor_conf.FUNCTION_REGISTER.keys())
        keys.sort()
        for datatype_name in keys:
            if datatype_name != editor_conf.UNBOUND_FUNCTION_DATATYPE and self.nodes_palette.data_type_filter:
                if not issubclass(self.nodes_palette.data_type_filter.get('class'), editor_conf.DataType.get_type(datatype_name).get('class')):
                    continue
            func_map = editor_conf.FUNCTION_REGISTER[datatype_name]
            func_signatures_list = func_map.keys()
            func_signatures_list = list(func_signatures_list) if not isinstance(func_signatures_list, list) else func_signatures_list
            for func_sign in func_signatures_list:
                expanded = self.nodes_palette.functions_first or bool(search_filter)
                func_dict = func_map[func_sign]
                icon_name = func_dict['icon']
                nice_name = func_dict.get('nice_name')
                sub_category_name = func_dict.get('category', 'General')
                palette_name = nice_name if nice_name else func_sign
                # Filter
                filter_matched = bool(search_filter) and (re.search(search_filter, palette_name, re.IGNORECASE)
                                                          is not None or re.search(search_filter, sub_category_name, re.IGNORECASE is not None))
                if search_filter and not filter_matched:
                    continue

                self.add_node_item(editor_conf.FUNC_NODE_ID,
                                   palette_name,
                                   func_signature=func_sign,
                                   category='Functions/{0}'.format(sub_category_name),
                                   icon_name=icon_name,
                                   expanded=expanded)


class PopupNodesPalette(QtWidgets.QDialog):

    @ classmethod
    def show_action(cls, owner, gr_view, shortcut=QtGui.QKeySequence(QtCore.Qt.Key_Tab)):
        action = QtWidgets.QAction(owner)
        action.setShortcut(shortcut)
        action.triggered.connect(lambda: cls.create(gr_view))
        return action

    @ classmethod
    def create(cls, gr_view):
        creator_dialog = cls(gr_view, parent=gr_view)
        creator_dialog.move(QtGui.QCursor.pos())
        creator_dialog.exec_()

    def __init__(self, view, parent=None, edge=None):
        super(PopupNodesPalette, self).__init__(parent)
        self.view = view
        self.scene = view.scene

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        data_type_filter = self.view.dragging.get_source_socket_datatype()
        self.nodes_palette = NodesPalette(icon_size=16, data_type_filter=data_type_filter, functions_first=True)
        self.nodes_palette.nodes_tree.setDragEnabled(False)
        self.nodes_palette.nodes_tree.installEventFilter(self)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.nodes_palette)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.nodes_palette.nodes_tree.itemClicked.connect(self.spawn_clicked_node)

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.KeyPress and \
                event.matches(QtGui.QKeySequence.InsertParagraphSeparator):
            item = self.nodes_palette.nodes_tree.currentItem()
            if item:
                self.spawn_clicked_node(item)
                return True
        return False

    def is_dragging_from_output(self):
        return self.view.dragging.drag_edge and self.view.dragging.drag_edge.start_socket

    def is_dragging_from_input(self):
        return self.view.dragging.drag_edge and self.view.dragging.drag_edge.end_socket

    def spawn_clicked_node(self, item):
        if not item.flags() & QtCore.Qt.ItemIsSelectable:
            return

        node_id = item.data(0, QLDragTreeWidget.NODE_ID_ROLE)
        json_data = item.data(0, QLDragTreeWidget.JSON_DATA_ROLE)
        new_node = self.scene.spawn_node_from_data(node_id, json_data, self.view.last_scene_mouse_pos)

        # Connect dragging edge
        # Output -> Input
        if self.is_dragging_from_output():
            start_socket = self.view.dragging.drag_edge.start_socket
            start_node = self.view.dragging.drag_edge.start_socket.node
            socket_to_connect = new_node.find_first_input_with_label(start_socket.label)
            if not socket_to_connect:
                socket_to_connect = new_node.find_first_input_of_datatype(start_socket.data_type)
            # Find exec sockets to connect
            if start_node.exec_out_socket and not start_node.exec_out_socket.has_edge() and new_node.exec_in_socket:
                node_edge.Edge(self.scene, start_socket=start_node.exec_out_socket, end_socket=new_node.exec_in_socket)
            # Finish dragging
            self.view.dragging.end_edge_drag(socket_to_connect)
        # Input -> Output
        elif self.is_dragging_from_input():
            end_socket = self.view.dragging.drag_edge.end_socket
            end_node = self.view.dragging.drag_edge.end_socket.node
            socket_to_connect = new_node.find_first_output_with_label(end_socket.label)
            if not socket_to_connect:
                socket_to_connect = new_node.find_first_output_of_datatype(end_socket.data_type)
            # Find exec sockets to connect
            if end_node.exec_in_socket and not end_node.exec_in_socket.has_edge() and new_node.exec_out_socket:
                node_edge.Edge(self.scene, start_socket=new_node.exec_out_socket, end_socket=end_node.exec_in_socket)
            self.view.dragging.end_edge_drag(socket_to_connect)

        self.close()
