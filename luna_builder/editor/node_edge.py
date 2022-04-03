import imp
from collections import OrderedDict

from luna import Logger
import luna.utils.enumFn as enumFn
import luna_builder.editor.graphics_edge as graphics_edge
import luna_builder.editor.node_serializable as node_serializable
import luna_builder.editor.node_socket as node_socket
imp.reload(graphics_edge)


class Edge(node_serializable.Serializable):

    class Type(enumFn.Enum):
        DIRECT = graphics_edge.QLGraphicsEdgeDirect
        BEZIER = graphics_edge.QLGraphicsEdgeBezier
        SQUARE = graphics_edge.QLGraphicsEdgeSquare

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self, scene, start_socket=None, end_socket=None, silent=False):
        super(Edge, self).__init__()
        self._start_socket = None
        self._end_socket = None
        self.scene = scene

        self.set_start_socket(start_socket, silent=silent)
        self.set_end_socket(end_socket, silent=silent)
        self.update_edge_graphics_type()
        self.scene.add_edge(self)

    @property
    def start_socket(self):
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        self.set_start_socket(value, silent=False)

    @property
    def end_socket(self):
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        self.set_end_socket(value, silent=False)

    @property
    def edge_type(self):
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        if isinstance(value, int):
            self._edge_type = list(Edge.Type)[value]
        elif isinstance(value, str):
            self._edge_type = Edge.Type[value]
        elif isinstance(value, Edge.Type):
            self._edge_type = value
        else:
            Logger.error('Invalid edge type value: {0}'.format(value))
            self._edge_type = Edge.Type.BEZIER

        if hasattr(self, 'gr_edge') and self.gr_edge is not None:
            self.scene.gr_scene.removeItem(self.gr_edge)

        self.gr_edge = self._edge_type.value(self)
        self.scene.gr_scene.addItem(self.gr_edge)
        if self.start_socket or self.end_socket:
            self.update_positions()

    def set_start_socket(self, value, silent=False):
        if value is not None and not isinstance(value, node_socket.Socket):
            Logger.error('Invalid value passed as start socket: {0}'.format(value))
            raise ValueError

        if self._start_socket is not None:
            self._start_socket.remove_edge(self, silent=silent)

        self._start_socket = value
        if self._start_socket is not None:
            self._start_socket.set_connected_edge(self, silent=silent)

    def set_end_socket(self, value, silent=False):
        if value is not None and not isinstance(value, node_socket.Socket):
            Logger.error('Invalid value passed as end socket: {0}'.format(value))
            raise ValueError

        if self._end_socket is not None:
            self._end_socket.remove_edge(self, silent=silent)

        self._end_socket = value
        if self._end_socket is not None:
            self._end_socket.set_connected_edge(self, silent=silent)

    def update_edge_graphics_type(self):
        self.edge_type = self.scene.edge_type

    def update_positions(self):
        if not hasattr(self, 'gr_edge'):
            return

        if self.start_socket is not None:
            source_pos = self.start_socket.get_position()
            source_pos[0] += self.start_socket.node.gr_node.pos().x()
            source_pos[1] += self.start_socket.node.gr_node.pos().y()
            self.gr_edge.set_source(*source_pos)

        if self.end_socket is not None:
            end_pos = self.end_socket.get_position()
            end_pos[0] += self.end_socket.node.gr_node.pos().x()
            end_pos[1] += self.end_socket.node.gr_node.pos().y()
            self.gr_edge.set_destination(*end_pos)

        if not self.start_socket:
            self.gr_edge.set_source(*end_pos)
        if not self.end_socket:
            self.gr_edge.set_destination(*source_pos)
        self.gr_edge.update()

    def remove_from_sockets(self, silent=False):
        self.set_start_socket(None, silent=silent)
        self.set_end_socket(None, silent=silent)

    def remove(self, silent=False):
        self.remove_from_sockets(silent=silent)
        self.scene.gr_scene.removeItem(self.gr_edge)
        self.gr_edge = None
        if self in self.scene.edges:
            self.scene.remove_edge(self)

    def get_other_socket(self, this_socket):
        result = None
        if this_socket is self.start_socket:
            result = self.end_socket
        elif this_socket is self.end_socket:
            result = self.start_socket
        return result

    def get_assigned_socket(self):
        if self.start_socket and self.end_socket:
            return (self.start_socket, self.end_socket)
        elif not self.end_socket:
            return self.start_socket
        else:
            return self.end_socket

    def serialize(self):
        return OrderedDict([
            ('id', self.uid),
            ('start', self.start_socket.uid),
            ('end', self.end_socket.uid)
        ])

    def deserialize(self, data, hashmap, restore_id=True):
        if restore_id:
            self.uid = data.get('id')
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.update_edge_graphics_type()
