import imp
from PySide2 import QtCore
from collections import deque
from collections import OrderedDict

from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.graphics_node as graphics_node
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.node_serializable as node_serializable
import luna_builder.editor.node_attrib_widget as node_attrib_widget
imp.reload(graphics_node)


class NodeSignals(QtCore.QObject):
    compiled_changed = QtCore.Signal(bool)
    invalid_changed = QtCore.Signal(bool)
    title_edited = QtCore.Signal(str)
    num_sockets_changed = QtCore.Signal()


class Node(node_serializable.Serializable):

    GRAPHICS_CLASS = graphics_node.QLGraphicsNode
    ATTRIB_WIDGET = node_attrib_widget.AttribWidget

    ID = None
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    DEFAULT_TITLE = 'Custom Node'
    TITLE_EDITABLE = False
    TITLE_COLOR = '#FF313131'
    MIN_WIDTH = 180
    MIN_HEIGHT = 30
    MAX_TEXT_WIDTH = 200
    INPUT_POSITION = node_socket.Socket.Position.LEFT_TOP.value
    OUTPUT_POSITION = node_socket.Socket.Position.RIGHT_TOP.value

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}> {2}".format(cls_name, nice_id, self.title)

    def __init__(self, scene, title=None):
        super(Node, self).__init__()
        self.scene = scene
        self.signals = NodeSignals()
        self._title = None
        self.inputs = []
        self.outputs = []
        self._required_inputs = deque()

        # Evaluation
        self._is_compiled = False
        self._is_invalid = False

        # Members init
        self.init_settings()
        self.init_inner_classes()
        self.title = title if title else self.__class__.DEFAULT_TITLE

        # Add to the scene
        self.scene.add_node(self)
        self.scene.gr_scene.addItem(self.gr_node)
        # Sockets
        self.signals.num_sockets_changed.connect(self.on_num_sockets_changed)
        self.init_sockets()
        self.create_connections()

    def init_settings(self):
        self.socket_spacing = 22

    def init_inner_classes(self):
        # Setup graphics
        self.gr_node = self.__class__.GRAPHICS_CLASS(self)

    def init_sockets(self, reset=True):
        self._required_inputs.clear()
        self.exec_in_socket = self.exec_out_socket = None
        if reset:
            self.remove_existing_sockets()

        # Create new sockets
        if self.__class__.IS_EXEC and self.__class__.AUTO_INIT_EXECS:
            self.exec_in_socket = self.add_input(editor_conf.DataType.EXEC)
            self.exec_out_socket = self.add_output(editor_conf.DataType.EXEC, max_connections=1)

    def create_connections(self):
        self.signals.compiled_changed.connect(self.on_compiled_change)
        self.signals.invalid_changed.connect(self.on_invalid_change)
        self.signals.title_edited.connect(self.on_title_edited)

    def remove_existing_sockets(self):
        if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
            for socket in self.inputs + self.outputs:
                self.scene.gr_scene.removeItem(socket.gr_socket)
            self.inputs = []
            self.outputs = []

    # ======= Properties ======= #

    @property
    def position(self):
        return self.gr_node.pos()

    def set_position(self, x, y):
        self.gr_node.setPos(x, y)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        old_height = self.gr_node.title_height
        old_width = self.gr_node.title_width
        self._title = value
        self.gr_node.title = self._title
        new_width = self.gr_node.title_width
        new_height = self.gr_node.title_height
        if old_height != new_height or old_width != new_width:
            self.update_size()

    # ======= Attrib widget ======= #
    def get_attrib_widget(self):
        return self.ATTRIB_WIDGET(self)

    # ======= Socket Utils ======= #

    def get_new_input_index(self):
        return len(self.inputs)

    def get_new_output_index(self):
        return len(self.outputs)

    def get_socket_position(self, index, position, count_on_this_side=1):
        if position in (node_socket.Socket.Position.LEFT_TOP, node_socket.Socket.Position.LEFT_CENTER, node_socket.Socket.Position.LEFT_BOTTOM):
            x = 0
        else:
            x = self.gr_node.width

        if position in (node_socket.Socket.Position.LEFT_BOTTOM, node_socket.Socket.Position.RIGHT_BOTTOM):
            # start from top
            y = self.gr_node.height - self.gr_node.edge_roundness - self.gr_node.title_horizontal_padding - index * self.socket_spacing
        elif position in (node_socket.Socket.Position.LEFT_CENTER, node_socket.Socket.Position.RIGHT_CENTER):
            num_sockets = count_on_this_side
            node_height = self.gr_node.height
            top_offset = self.gr_node.title_height + 2 * self.gr_node.title_vertical_padding + self.gr_node.edge_padding
            available_height = node_height - top_offset

            y = top_offset + available_height / 2.0 + (index - 0.5) * self.socket_spacing
            if num_sockets > 1:
                y -= self.socket_spacing * (num_sockets - 1) / 2

        elif position in (node_socket.Socket.Position.LEFT_TOP, node_socket.Socket.Position.RIGHT_TOP):
            # start from bottom
            y = self.gr_node.title_height + self.gr_node.title_horizontal_padding + self.gr_node.edge_roundness + index * self.socket_spacing
        else:
            y = 0

        return [x, y]

    def recalculate_height(self):

        max_inputs = len(self.inputs) * self.socket_spacing
        max_outputs = len(self.outputs) * self.socket_spacing
        total_socket_height = max(max_inputs, max_outputs, self.MIN_HEIGHT)
        self.gr_node.height = total_socket_height + self.gr_node.title_height + self.gr_node.lower_padding

    def recalculate_width(self):
        # Labels max width
        input_widths = [socket.get_label_width() for socket in self.inputs] or [0, 0]
        output_widths = [socket.get_label_width() for socket in self.outputs] or [0, 0]

        max_label_width = max(input_widths + output_widths)

        # Calculate clamped title text width
        self.gr_node.title_item.setTextWidth(-1)
        if self.gr_node.title_width > self.MAX_TEXT_WIDTH:
            self.gr_node.title_item.setTextWidth(self.MAX_TEXT_WIDTH)
            title_with_padding = self.MAX_TEXT_WIDTH + self.gr_node.title_horizontal_padding * 2
        else:
            title_with_padding = self.gr_node.title_width + self.gr_node.title_horizontal_padding * 2

        # Use the max value between widths of label, allowed min width, clamped text width
        # Sockets on both sides or only one side
        if self.inputs and self.outputs:
            self.gr_node.width = max(max_label_width * 2, self.MIN_WIDTH, title_with_padding)
        else:
            self.gr_node.width = max(max_label_width + self.gr_node.one_side_horizontal_padding, self.MIN_WIDTH, title_with_padding)

    # ======== Update methods ========= #
    def append_tooltip(self, text):
        self.gr_node.setToolTip(self.gr_node.toolTip() + text)

    def update_connected_edges(self):
        for socket in self.inputs + self.outputs:
            socket.update_edges()

    def update_socket_positions(self):
        for socket in self.outputs + self.inputs:
            socket.update_positions()

    def update_size(self):
        self.recalculate_width()
        self.recalculate_height()
        self.update_socket_positions()
        self.update_connected_edges()

    def on_num_sockets_changed(self):
        self.update_size()

    def remove(self, silent=False):
        try:
            self.remove_all_connections(include_exec=True, silent=silent)
            self.scene.gr_scene.removeItem(self.gr_node)
            self.gr_node = None
            self.scene.remove_node(self)
        except Exception:
            Logger.exception('Failed to delete node {0}'.format(self))

    # ========= Evaluation ============= #
    def remove_all_connections(self, include_exec=False, silent=False):
        for socket in self.inputs + self.outputs:
            if not include_exec and socket.data_type == editor_conf.DataType.EXEC:
                continue
            socket.remove_all_edges(silent=silent)

    def is_compiled(self):
        return self._is_compiled

    def set_compiled(self, value=False):
        if self._is_compiled == value:
            return
        self._is_compiled = value
        self.signals.compiled_changed.emit(self._is_compiled)

    def on_compiled_change(self, state):
        self.mark_children_compiled(state)

    def is_invalid(self):
        return self._is_invalid

    def set_invalid(self, value=True):
        self._is_invalid = value
        self.signals.invalid_changed.emit(self._is_invalid)

    def verify_inputs(self):
        invalid_inputs = deque()
        for socket in self._required_inputs:
            if not socket.has_edge() and not socket.value():
                invalid_inputs.append(socket)
        if invalid_inputs:
            tool_tip = ''
            for socket in invalid_inputs:
                tool_tip += 'Invalid input: {0}\n'.format(socket.label)
            self.append_tooltip(tool_tip)
            return False
        return True

    def verify(self):
        self.gr_node.setToolTip('')
        result = self.verify_inputs()

        return result

    def on_invalid_change(self, state):
        if state:
            Logger.debug('{0} marked invalid'.format(self))

    def mark_children_compiled(self, state):
        if state:
            return
        for child_node in self.list_children():
            child_node.set_compiled(state)
            child_node.mark_children_compiled(state)

    # ========= Interaction methods ========== #
    def edit_title(self):
        if self.TITLE_EDITABLE:
            self.gr_node.title_item.edit()
        else:
            Logger.warning('Title for node {0} is not editable'.format(self.title))

    def on_title_edited(self, new_title):
        if not new_title:
            new_title = self.DEFAULT_TITLE
        old_title = self.title
        self.title = new_title
        self.scene.history.store_history('Renamed node {0}->{1}'.format(old_title, new_title))

    # ========= Serialization methods ========== #

    def pre_deserilization(self, data):
        pass

    def post_deserilization(self, data):
        pass

    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs:
            inputs.append(socket.serialize())
        for socket in self.outputs:
            outputs.append(socket.serialize())

        return OrderedDict([
            ('id', self.uid),
            ('node_id', self.__class__.ID),
            ('title', self.title),
            ('pos_x', self.gr_node.scenePos().x()),
            ('pos_y', self.gr_node.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs)
        ])

    def deserialize(self, data, hashmap, restore_id=True):
        # Pre
        self.pre_deserilization(data)

        # Desereialization
        if restore_id:
            self.uid = data.get('id')
        hashmap[data['id']] = self

        self.set_position(data['pos_x'], data['pos_y'])
        self.title = data.get('title')

        # Sockets
        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)

        # Deserialize sockets
        for socket_data in data.get('inputs'):
            found = None  # type: node_socket.Socket
            for socket in self.inputs:
                if socket.index == socket_data['index']:
                    found = socket
                    break
            if found is None:
                Logger.warning('Deserialization of socket data has not found socket with index {0}'.format(socket_data['index']))
                Logger.debug('Missing socket data: {0}'.format(socket_data))
                data_type = editor_conf.DataType.get_type(socket_data['data_type'])
                value = socket_data.get('value', data_type['default'])
                found = self.add_input(data_type, socket_data['label'], value=value)
            found.deserialize(socket_data, hashmap, restore_id)

        for socket_data in data.get('outputs'):
            found = None
            for socket in self.outputs:
                if socket.index == socket_data['index']:
                    found = socket
                    break
            if found is None:
                Logger.warning('Deserialization of socket data has not found socket with index {0}'.format(socket_data['index']))
                Logger.debug('Missing socket data: {0}'.format(socket_data))
                # we can create new socket for this
                data_type = editor_conf.DataType.get_type(socket_data['data_type'])
                value = socket_data.get('value', data_type['default'])
                found = self.add_output(data_type, socket_data['label'], value=value)
            found.deserialize(socket_data, hashmap, restore_id)
        self.signals.num_sockets_changed.emit()
        # Post
        self.post_deserilization(data)

    # ========= Socket creation methods ========== #
    def add_input(self, data_type, label=None, value=None, *args, **kwargs):
        socket = node_socket.InputSocket(self,
                                         index=self.get_new_input_index(),
                                         position=self.__class__.INPUT_POSITION,
                                         data_type=data_type,
                                         label=label,
                                         max_connections=1,
                                         value=value,
                                         count_on_this_side=self.get_new_input_index(),
                                         *args,
                                         **kwargs)
        self.inputs.append(socket)
        self.signals.num_sockets_changed.emit()
        return socket

    def add_output(self, data_type, label=None, max_connections=0, value=None, *args, **kwargs):
        if data_type == editor_conf.DataType.EXEC:
            max_connections = 1
        socket = node_socket.OutputSocket(self,
                                          index=self.get_new_output_index(),
                                          position=self.__class__.OUTPUT_POSITION,
                                          data_type=data_type,
                                          label=label,
                                          max_connections=max_connections,
                                          value=value,
                                          count_on_this_side=self.get_new_output_index(),
                                          *args,
                                          **kwargs)
        self.outputs.append(socket)
        self.signals.num_sockets_changed.emit()
        return socket

    def remove_socket(self, name, is_input=True):
        try:
            if is_input:
                socket_to_remove = [socket for socket in self.inputs if socket.label == name][0]  # type: node_socket.InputSocket
                self.inputs.remove(socket_to_remove)
                if socket_to_remove in self._required_inputs:
                    self._required_inputs.remove(socket_to_remove)
                for index, socket in enumerate(self.inputs):
                    socket.index = index
            else:
                socket_to_remove = [socket for socket in self.outputs if socket.label == name][0]  # type: node_socket.OutputSocket
                self.outputs.remove(socket_to_remove)
                for index, socket in enumerate(self.outputs):
                    socket.index = index
            socket_to_remove.remove()
            self.signals.num_sockets_changed.emit()
        except Exception:
            Logger.error('Failed to delete socket {0}'.format(name))

    # ========= Graph Traversal ================ #

    def list_children(self, recursive=False):
        children = []
        for output in self.outputs:
            for child_socket in output.list_connections():
                children.append(child_socket.node)
        if recursive:
            for child_node in children:
                children += child_node.list_children(recursive=True)

        return children

    def list_exec_children(self):
        exec_children = []
        for exec_out in self.list_exec_outputs():
            exec_children += [socket.node for socket in exec_out.list_connections()]
        return exec_children

    def get_exec_queue(self):
        exec_queue = deque([self])

        for exec_out in self.list_exec_outputs():
            if not exec_out.list_connections():
                continue
            exec_queue.extend(exec_out.list_connections()[0].node.get_exec_queue())

        return exec_queue

    def update_affected_outputs(self):
        for input in self.inputs:
            input.update_affected()

    def _exec(self):
        Logger.debug('Executing {0}...'.format(self))
        try:
            self.execute()
            self.update_affected_outputs()
        except Exception:
            Logger.exception('Failed to execute {0} {1}'.format(self.title, self))
            self.append_tooltip('Execution error (Check script editor for details)\n')
            self.set_invalid(True)
            raise

        self.set_compiled(True)
        self.set_invalid(False)
        return 0

    def execute(self):
        return 0

    def exec_children(self):
        for node in self.list_exec_children():
            node._exec()

    # ========= Socket finding/data retriving ========= #
    def mark_inputs_required(self, inputs):
        for socket in inputs:
            self.mark_input_as_required(socket)

    def mark_input_as_required(self, input_socket):
        if isinstance(input_socket, node_socket.InputSocket):
            self._required_inputs.append(input_socket)
        elif isinstance(input_socket, str):
            socket = self.find_first_input_with_label(input_socket)
            if not input_socket:
                Logger.error('Can not mark input {0} as required. Failed to find socket from label.'.format(input_socket))
                return
            self._required_inputs.append(socket)
        else:
            Logger.error('Invalid required "input socket" argument {0}'.format(input_socket))

    def find_first_input_with_label(self, text):
        result = None
        for socket in self.inputs:
            if socket.label == text:
                result = socket
                break
        return result

    def find_first_input_of_datatype(self, datatype):
        result = None
        for socket in self.inputs:
            if issubclass(datatype.get('class', type(None)), socket.data_class):
                result = socket
                break
        return result

    def find_first_output_with_label(self, text):
        result = None
        for socket in self.outputs:
            if socket.label == text:
                result = socket
                break
        return result

    def find_first_output_of_datatype(self, datatype):
        result = None
        for socket in self.outputs:
            if issubclass(socket.data_class, datatype.get('class', type(None))):
                result = socket
                break
        return result

    def get_value(self, socket_name):
        socket = getattr(self, socket_name)
        if not isinstance(socket, node_socket.Socket):
            Logger.error('Socket {0} does not exist.'.format(socket_name))
            raise AttributeError
        return socket.value()

    def list_exec_outputs(self):
        return [socket for socket in self.outputs if socket.data_type == editor_conf.DataType.EXEC]

    def list_non_exec_inputs(self):
        return [socket for socket in self.inputs if socket.data_type != editor_conf.DataType.EXEC]

    def list_non_exec_outputs(self):
        return [socket for socket in self.outputs if socket.data_type != editor_conf.DataType.EXEC]
