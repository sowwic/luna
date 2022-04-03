from PySide2 import QtWidgets
from collections import OrderedDict

from luna import Logger
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.editor_conf as editor_conf


class AttribWidget(QtWidgets.QGroupBox):

    IGNORED_DATA_TYPES = [editor_conf.DataType.EXEC, editor_conf.DataType.LIST]
    IGNORED_CLASSES = [dt['class'] for dt in IGNORED_DATA_TYPES]

    def __init__(self, node, parent=None):
        super(AttribWidget, self).__init__(parent)
        self.node = node
        self.setTitle(self.node.DEFAULT_TITLE)
        self.fields_map = OrderedDict()

        self.main_layout = QtWidgets.QFormLayout()
        self.setLayout(self.main_layout)

        # On creation
        self.init_fields()
        self.update_fields()
        self.create_signal_connections()

    def showEvent(self, event):
        super(AttribWidget, self).showEvent(event)
        self.update_fields()

    def init_fields(self):
        self.fields_map.clear()
        socket_list = self.node.list_non_exec_inputs()
        if not socket_list:
            socket_list = self.node.list_non_exec_outputs()

        for socket in socket_list:
            try:
                if any([issubclass(socket.data_class, dt_class) for dt_class in self.__class__.IGNORED_CLASSES]):
                    continue

                widget = None
                if issubclass(socket.data_class, editor_conf.DataType.STRING.get('class')):
                    widget = QtWidgets.QLineEdit()
                elif issubclass(socket.data_class, editor_conf.DataType.BOOLEAN.get('class')):
                    widget = QtWidgets.QCheckBox()
                elif issubclass(socket.data_class, editor_conf.DataType.NUMERIC.get('class')):
                    widget = QtWidgets.QDoubleSpinBox()
                    widget.setRange(-9999, 9999)
                # elif issubclass(socket.data_class, editor_conf.DataType.LIST.get('class')):
                #     widget = QtWidgets.QListWidget()
                elif issubclass(socket.data_class, editor_conf.DataType.CONTROL.get('class')):
                    widget = QtWidgets.QLineEdit()
                elif issubclass(socket.data_class, editor_conf.DataType.COMPONENT.get('class')):
                    widget = QtWidgets.QLineEdit()
                else:
                    Logger.error('Failed to create attribute field: {0}::{1}'.format(socket, socket.data_class))
                if widget:
                    # Store in the map and add to layout
                    self.store_in_fields_map(socket, widget)
                    self.main_layout.addRow(socket.label, widget)
                # Signals
            except Exception:
                Logger.exception('Attribute field add exception')

    def store_in_fields_map(self, socket, widget):
        self.fields_map[socket.label] = (socket, widget)

    def create_signal_connections(self):
        for label, socket_widget_pair in self.fields_map.items():
            socket, widget = socket_widget_pair
            if isinstance(socket, node_socket.InputSocket):
                socket.signals.connection_changed.connect(self.update_fields)
            if socket.is_runtime_data():
                continue

            # Setable types
            if isinstance(widget, QtWidgets.QLineEdit):
                widget.textChanged.connect(socket.set_value)
            elif isinstance(widget, QtWidgets.QAbstractSpinBox):
                widget.valueChanged.connect(socket.set_value)
            elif isinstance(widget, QtWidgets.QCheckBox):
                widget.toggled.connect(socket.set_value)

    def update_widget_value(self, socket, widget):
        try:
            if issubclass(socket.data_class, editor_conf.DataType.STRING.get('class')):
                widget.setText(socket.value())
            elif issubclass(socket.data_class, editor_conf.DataType.BOOLEAN.get('class')):
                widget.setChecked(socket.value())
            elif issubclass(socket.data_class, editor_conf.DataType.NUMERIC.get('class')):
                if socket.value():
                    widget.setValue(socket.value())
            # elif issubclass(socket.data_class, editor_conf.DataType.LIST.get('class')):
            elif issubclass(socket.data_class, editor_conf.DataType.CONTROL.get('class')):
                if socket.value():
                    widget.setText(str(socket.value().transform))
                else:
                    widget.clear()
            elif issubclass(socket.data_class, editor_conf.DataType.COMPONENT.get('class')):
                if socket.value():
                    if hasattr(socket.value(), 'pynode'):
                        widget.setText(str(socket.value().pynode.name()))
                    else:
                        widget.setText(str(socket.value()))
            else:
                Logger.error('Failed to create attribute field: {0}::{1}'.format(socket, socket.data_class))
        except Exception:
            Logger.exception('Failed to update widget value for {0}'.format(socket))

    def update_fields(self):
        self.blockSignals(True)
        for label, socket_widget_pair in self.fields_map.items():
            socket, widget = socket_widget_pair
            self.update_widget_value(socket, widget)
            if isinstance(socket, node_socket.InputSocket):
                widget.setEnabled(not socket.has_edge())
        self.blockSignals(False)
