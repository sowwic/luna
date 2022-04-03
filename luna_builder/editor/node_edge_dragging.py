from luna import Logger
import luna_builder.editor.graphics_socket as graphics_socket
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.node_edge as node_edge


class EdgeDrag(object):
    def __init__(self, gr_view):
        self.gr_view = gr_view
        self.drag_edge = None
        self.drag_start_socket = None

    def get_source_socket_datatype(self):
        if not self.drag_start_socket:
            return None
        return self.drag_start_socket.data_type

    def update_positions(self, x, y):
        if self.drag_edge is not None and self.drag_edge.gr_edge is not None:
            if self.drag_edge.start_socket:
                self.drag_edge.gr_edge.set_destination(x, y)
            else:
                self.drag_edge.gr_edge.set_source(x, y)
            self.drag_edge.gr_edge.update()
        else:
            Logger.error('Tried to update self.drag_edge.gr_edge, but it is None')

    def start_edge_drag(self, item):
        try:
            Logger.debug('Start dragging edge: {}'.format(self.gr_view.edge_mode))
            self.drag_start_socket = item.socket
            if isinstance(item.socket, node_socket.OutputSocket):
                Logger.debug('Assign start socket to: {0}'.format(item.socket))
                self.drag_edge = node_edge.Edge(self.gr_view.scene, start_socket=item.socket, end_socket=None, silent=True)
            else:
                Logger.debug('Assign end socket to: {0}'.format(item.socket))
                self.drag_edge = node_edge.Edge(self.gr_view.scene, start_socket=None, end_socket=item.socket, silent=True)
        except Exception:
            Logger.exception('Start edge drag exception')

    def end_edge_drag(self, item):
        if isinstance(item, node_socket.Socket):
            item = item.gr_socket

        self.gr_view.reset_edge_mode()
        self.drag_edge.remove(silent=True)
        self.drag_edge = None

        # Non socket click or can't be connected
        if not isinstance(item, graphics_socket.QLGraphicsSocket) or not item.socket.can_be_connected(self.drag_start_socket):
            Logger.debug("Canceling edge dragging")
            self.drag_start_socket = None
            return False

        # Another connectable socket clicked
        try:
            start_socket = None
            end_socket = None
            if isinstance(item.socket, node_socket.OutputSocket):
                Logger.debug('Assign start socket: {0}'.format(item.socket))
                start_socket = item.socket
                end_socket = self.drag_start_socket
            elif isinstance(item.socket, node_socket.InputSocket):
                Logger.debug('Assign end socket: {0}'.format(item.socket))
                start_socket = self.drag_start_socket
                end_socket = item.socket

            new_edge = node_edge.Edge(self.gr_view.scene, start_socket=start_socket, end_socket=end_socket)
            self.drag_start_socket = None
            Logger.debug('EdgeDrag: created new edge {0} -> {1}'.format(new_edge.start_socket, new_edge.end_socket))
            self.gr_view.scene.history.store_history('Edge created by dragging', set_modified=True)
            return True

        except Exception:
            Logger.exception('End edge drag exception')
            return False
