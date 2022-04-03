import imp
import pymel.core as pm
from PySide2 import QtCore
from collections import OrderedDict

from luna import Logger
import luna.utils.enumFn as enumFn
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.graphics_socket as graphics_socket
import luna_builder.editor.node_serializable as node_serializable
imp.reload(graphics_socket)


class SocketSignals(QtCore.QObject):
    value_changed = QtCore.Signal()
    connection_changed = QtCore.Signal()


class Socket(node_serializable.Serializable):

    class Position(enumFn.Enum):
        LEFT_TOP = 1
        LEFT_CENTER = 2
        LEFT_BOTTOM = 3
        RIGHT_TOP = 4
        RIGHT_CENTER = 5
        RIGHT_BOTTOM = 6

    LABEL_VERTICAL_PADDING = -10.0

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self,
                 node,
                 index=0,
                 position=Position.LEFT_TOP,
                 data_type=editor_conf.DataType.NUMERIC,
                 label=None,
                 max_connections=0,
                 value=None,
                 count_on_this_side=0):
        super(Socket, self).__init__()
        self.signals = SocketSignals()
        self.edges = []
        self._affected_sockets = []

        self.node = node
        self.index = index
        self.node_position = position if isinstance(position, Socket.Position) else Socket.Position(position)
        # self.data_type = editor_conf.DataType.get_type(data_type) if isinstance(data_type, int) else data_type
        self.data_type = data_type
        self._label = label if label is not None else self.data_type.get('label')
        self.max_connections = max_connections
        self.count_on_this_side = count_on_this_side
        self._value = self.data_type.get('default') if value is None else value
        self._default_value = self.value()

        # Graphics
        self.gr_socket = graphics_socket.QLGraphicsSocket(self)
        self.update_positions()

        # Signals
        self.create_connections()

    def create_connections(self):
        pass

    # ============ Properties ============= #

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, text):
        self._label = text
        self.gr_socket.text_item.setPlainText(self._label)

    @property
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = value

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        if isinstance(value, str):
            self._data_type = editor_conf.DATATYPE_REGISTER[value]
        elif isinstance(value, dict):
            self._data_type = value
        else:
            Logger.error('{0}: Can\'t set datatype to {0}'.format(value))
            raise ValueError
        if hasattr(self, 'gr_socket'):
            self.gr_socket._color_background = self._data_type.get('color')
            self.gr_socket.update()
        self.node.update_size()

    @ property
    def data_class(self):
        return self.data_type.get('class')

    # ============ Basic methods ============= #
    def remove(self):
        self.remove_all_edges()
        self.node.scene.gr_scene.removeItem(self.gr_socket)

    # ============ Datatype methods ============= #

    def is_runtime_data(self):
        runtime_classes = editor_conf.DataType.runtime_types(classes=True)
        return self.data_class in runtime_classes or self.value().__class__ in runtime_classes
    # ============ Value methods ============= #

    def value(self):
        return self._value

    def set_value(self, value):
        if self.data_type == editor_conf.DataType.EXEC:
            return
        if self._value == value:
            return
        if isinstance(value, pm.PyNode):
            value = str(value)

        self._value = value
        self.signals.value_changed.emit()

    def reset_value_to_default(self):
        self.set_value(self.default_value)

    def affects(self, other_socket):
        self._affected_sockets.append(other_socket)

    # ============ Graphics objects methods ============= #

    def update_positions(self):
        self.gr_socket.setPos(*self.node.get_socket_position(self.index, self.node_position, self.count_on_this_side))
        self.gr_socket.text_item.setPos(*self.get_label_position())

    def get_position(self):
        return self.node.get_socket_position(self.index, self.node_position, self.count_on_this_side)

    def get_label_position(self):
        text_width = self.gr_socket.text_item.boundingRect().width()
        if self.node_position in [Socket.Position.LEFT_TOP, Socket.Position.LEFT_BOTTOM]:
            return [self.node.gr_node.width / 25.0, Socket.LABEL_VERTICAL_PADDING]
        else:
            return [-text_width - self.node.gr_node.width / 25, Socket.LABEL_VERTICAL_PADDING]

    def get_label_width(self):
        return self.gr_socket.text_item.boundingRect().width()

    # ============ Edge Methods ============= #

    def has_edge(self):
        return bool(self.edges)

    def set_connected_edge(self, edge, silent=False):
        if not edge:
            Logger.warning('{0}: Recieved edge {1}'.format(self, edge))
            return

        if self.edges and self.max_connections and len(self.edges) >= self.max_connections:
            self.edges[-1].remove()
        self.edges.append(edge)

        if not silent:
            self.signals.connection_changed.emit()

    def remove_all_edges(self, silent=False):
        while self.edges:
            self.edges[0].remove(silent=silent)
        self.edges = []

    def get_invalid_edges(self):
        return [edge for edge in self.edges if not self.can_be_connected(edge.get_other_socket(self))]

    def remove_edge(self, edge, silent=False):
        self.edges.remove(edge)
        if not silent:
            self.signals.connection_changed.emit()

    def update_edges(self):
        for edge in self.edges:
            edge.update_positions()

    # ============ Connections methods ============= #
    def can_be_connected(self, other_socket):
        # Clicking on socket edge is dragging from
        if self is other_socket:
            return False

        # Trying to connect output->output or input->input
        if isinstance(other_socket, self.__class__):
            Logger.warning('Can\'t connect two sockets of the same type')
            return False

        if self.node is other_socket.node:
            Logger.warning('Can\'t connect sockets on the same node')
            return False

        return True

    def list_connections(self):
        result = []
        for edge in self.edges:
            for socket in [edge.start_socket, edge.end_socket]:
                if socket and socket != self:
                    result.append(socket)
        return result

    # ============ (De)Serialization ============= #
    def serialize(self):
        if self.is_runtime_data():
            value = None
        else:
            value = self.value()

        return OrderedDict([
            ('id', self.uid),
            ('index', self.index),
            ('position', self.node_position.value),
            ('data_type', editor_conf.DataType.get_type_name(self.data_type)),
            ('max_connections', self.max_connections),
            ('label', self.label),
            ('value', value)
        ])

    def deserialize(self, data, hashmap, restore_id=True):
        if restore_id:
            self.uid = data['id']
        data_type = editor_conf.DataType.get_type(data['data_type'])
        value = data.get('value', data_type['default'])
        self.data_type = data_type
        self.set_value(value)
        hashmap[data['id']] = self
        return True

    def update_affected(self):
        for socket in self._affected_sockets:
            socket.set_value(self.value())


class InputSocket(Socket):

    def create_connections(self):
        super(InputSocket, self).create_connections()
        self.signals.value_changed.connect(self.node.set_compiled)
        self.signals.connection_changed.connect(self.on_connection_changed)

    def can_be_connected(self, other_socket):
        result = super(InputSocket, self).can_be_connected(other_socket)
        if not issubclass(other_socket.data_class, self.data_class):
            return False
        return result

    def value(self):
        if self.has_edge():
            output_socket = self.edges[0].get_other_socket(self)
            if output_socket:
                return output_socket.value()
        return self._value

    def on_connection_changed(self):
        if not self.has_edge() and self.is_runtime_data():
            self.set_value(self.data_type['default'])


class OutputSocket(Socket):
    def create_connections(self):
        super(OutputSocket, self).create_connections()
        self.signals.value_changed.connect(self.notify_connected_inputs_value)

    def can_be_connected(self, other_socket):
        result = super(OutputSocket, self).can_be_connected(other_socket)
        if not issubclass(self.data_class, other_socket.data_class):
            return False
        return result

    def notify_connected_inputs_value(self):
        for socket in self.list_connections():
            socket.signals.value_changed.emit()
