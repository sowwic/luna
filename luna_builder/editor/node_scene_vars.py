import json
from collections import OrderedDict
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from luna import Logger
import luna.utils.pysideFn as pysideFn
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.node_serializable as node_serializable


class VarsSignals(QtCore.QObject):
    value_changed = QtCore.Signal(str)
    data_type_changed = QtCore.Signal(str)


class SceneVars(node_serializable.Serializable):
    def __init__(self, scene):
        super(SceneVars, self).__init__()
        self.scene = scene
        self.signals = VarsSignals()
        self._vars = OrderedDict()
        self.create_connections()

    def create_connections(self):
        self.signals.data_type_changed.connect(self.update_setters)
        self.signals.data_type_changed.connect(self.update_getters)

    def get_value(self, name):
        return self._vars[name][0]

    def set_value(self, name, value):
        self._vars[name][0] = value
        self.signals.value_changed.emit(name)

    def get_data_type(self, name, as_dict=False):
        typ_name = self._vars[name][1]
        if not as_dict:
            return typ_name
        return editor_conf.DATATYPE_REGISTER[typ_name]

    def set_data_type(self, name, typ_name):
        self._vars[name][0] = editor_conf.DATATYPE_REGISTER[typ_name]['default']
        self._vars[name][1] = typ_name
        self.signals.data_type_changed.emit(name)
        self.scene.history.store_history('Variable {0} data type changed to {1}'.format(name, typ_name))

    def unique_var_name(self, name):
        index = 1
        if name in self._vars.keys():
            while '{0}{1}'.format(name, index) in self._vars.keys():
                index += 1
            name = '{0}{1}'.format(name, index)
        return name

    def add_new_var(self, name):
        name = self.unique_var_name(name)
        self._vars[name] = [0.0, 'NUMERIC']
        self.scene.history.store_history('Added variable {0}'.format(name))

    def delete_var(self, var_name):
        if var_name not in self._vars.keys():
            Logger.error("Can't delete non existing variable {0}".format(var_name))
            return
        for node in self.list_setters(var_name) + self.list_getters(var_name):
            node.set_invalid(True)
        self._vars.pop(var_name)
        self.scene.history.store_history('Deleted variable {0}'.format(var_name))

    def rename_var(self, old_name, new_name):
        new_name = self.unique_var_name(new_name)
        old_value = self._vars[old_name]
        self._vars = OrderedDict([(new_name, old_value) if k == old_name else (k, v) for k, v in self._vars.items()])
        for node in self.list_setters(old_name) + self.list_getters(old_name):
            node.set_var_name(new_name)
        self.scene.history.store_history('Renamed variable {0} -> {1}'.format(old_name, new_name))

    def list_setters(self, var_name):
        return [node for node in self.scene.nodes if node.ID == editor_conf.SET_NODE_ID and node.var_name == var_name]

    def list_getters(self, var_name):
        return [node for node in self.scene.nodes if node.ID == editor_conf.GET_NODE_ID and node.var_name == var_name]

    def update_setters(self, var_name):
        try:
            for setter_node in self.list_setters(var_name):
                setter_node.update()
        except Exception:
            Logger.exception('Failed to update getters')

    def update_getters(self, var_name):
        try:
            for getter_node in self.list_getters(var_name):
                getter_node.update()
        except Exception:
            Logger.exception('Failed to update setters')

    def serialize(self):
        try:
            result = OrderedDict()
            for var_name, value_type_pair in self._vars.items():
                value, type_name = value_type_pair
                if type_name in editor_conf.DataType.runtime_types(names=True):
                    result[var_name] = [editor_conf.DATATYPE_REGISTER[type_name]['default'], type_name]
                else:
                    result[var_name] = [value, type_name]
        except Exception:
            Logger.exception('ScenVars serialize exception')
            raise
        return result

    def deserialize(self, data):
        # Direct assignment of _vars = data results in KeyError
        self._vars.clear()
        self._vars.update(data)


class SceneVarsWidget(QtWidgets.QWidget):

    JSON_DATA_ROLE = QtCore.Qt.UserRole + 1

    def __init__(self, main_window, parent=None):
        super(SceneVarsWidget, self).__init__(parent)
        self.main_window = main_window
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    @property
    def scene_vars(self):
        if not self.main_window.current_editor:
            return None
        return self.main_window.current_editor.scene.vars

    @property
    def attrib_editor(self):
        return self.main_window.attrib_editor

    def create_widgets(self):
        self.var_list = QLVarsListWidget(self)
        self.add_var_btn = QtWidgets.QPushButton()
        self.delete_var_btn = QtWidgets.QPushButton()
        self.add_var_btn.setIcon(pysideFn.get_QIcon('plus.png'))
        self.delete_var_btn.setIcon(pysideFn.get_QIcon('delete.png'))

    def create_layouts(self):
        buttons_layout = QtWidgets.QHBoxLayout()
        # buttons_layout.addStretch()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(2)
        buttons_layout.addWidget(self.add_var_btn)
        buttons_layout.addWidget(self.delete_var_btn)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addLayout(buttons_layout)
        self.main_layout.addWidget(self.var_list)

    def create_connections(self):
        self.add_var_btn.clicked.connect(self.add_variable)
        self.delete_var_btn.clicked.connect(self.delete_selected_var)

    def add_variable(self):
        if not self.scene_vars:
            return
        self.scene_vars.add_new_var('variable')
        self.update_var_list()

    def delete_selected_var(self):
        sel = self.var_list.selectedItems()
        if not sel:
            return

        try:
            var_name = sel[-1].data(QLVarsListWidget.JSON_DATA_ROLE)['var_name']
            if not self.scene_vars:
                Logger.error('Scene vars is {0}, cant delete'.format(self.scene_vars))
                return
            self.scene_vars.delete_var(var_name)
            self.update_var_list()
            self.attrib_editor.update_current_var_widget(None)
        except Exception:
            Logger.exception('Delete selected var exception')

    def update_var_list(self):
        self.var_list.populate()


class QLVarsListWidget(QtWidgets.QListWidget):

    variable_renamed = QtCore.Signal(QtWidgets.QListWidgetItem)

    PIXMAP_ROLE = QtCore.Qt.UserRole
    JSON_DATA_ROLE = QtCore.Qt.UserRole + 1

    def __init__(self, vars_widget, parent=None):
        super(QLVarsListWidget, self).__init__(parent)
        self.vars_widget = vars_widget

        # self.setIconSize(self.nodes_palette.icon_size)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.create_connections()

    @property
    def scene_vars(self):
        return self.vars_widget.scene_vars

    def create_connections(self):
        self.itemDoubleClicked.connect(self.editItem)
        self.itemChanged.connect(self.on_item_changed)
        self.variable_renamed.connect(self.vars_widget.attrib_editor.update_current_var_widget)

    def on_item_changed(self, item):
        json_data = item.data(QLVarsListWidget.JSON_DATA_ROLE)
        if not json_data:
            return

        old_var_name = json_data['var_name']

        # Handle empty name
        if not item.text().strip():
            item.setText(old_var_name)

        # Compare item new and old var names
        if item.text() == old_var_name:
            return
        # Do renaming if was changed
        old_row = self.row(item)
        self.scene_vars.rename_var(old_var_name, item.text())
        # Repopulate
        self.populate()
        new_item = self.item(old_row)
        self.variable_renamed.emit(new_item)

    def populate(self):
        self.clear()
        if not self.scene_vars or not self.scene_vars._vars:
            return

        for var_name, value_dt_pair in self.scene_vars._vars.items():
            new_item = QtWidgets.QListWidgetItem()
            new_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable)
            new_item.setText(var_name)
            # new_item.setIcon()
            new_item.setSizeHint(QtCore.QSize(16, 16))
            json_data = {'var_name': var_name}
            new_item.setData(QLVarsListWidget.JSON_DATA_ROLE, json_data)
            self.addItem(new_item)

    def startDrag(self, event):
        Logger.debug('Vars::startDrag')
        try:
            item = self.currentItem()  # type: QtWidgets.QTreeWidgetItem

            # Pack data to json
            json_data = item.data(QLVarsListWidget.JSON_DATA_ROLE)

            # Pack data to data stream
            item_data = QtCore.QByteArray()
            data_stream = QtCore.QDataStream(item_data, QtCore.QIODevice.WriteOnly)
            data_stream.writeQString(json.dumps(json_data))

            # Create mime data
            mime_data = QtCore.QMimeData()
            mime_data.setData(editor_conf.VARS_MIMETYPE, item_data)

            # Create drag
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)
            # drag.setHotSpot(QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2))
            # drag.setPixmap(pixmap)

            Logger.debug('Dragging item <{0}>'.format(item.text()))
            drag.exec_(QtCore.Qt.MoveAction)

        except Exception:
            Logger.exception('Vars drag exception')


class VarAttribWidget(QtWidgets.QGroupBox):

    data_type_switched = QtCore.Signal(QtWidgets.QListWidgetItem, str)

    def __init__(self, list_item, scene, parent=None):
        super(VarAttribWidget, self).__init__(parent)
        self.list_item = list_item  # type: QtWidgets.QListWidgetItem
        self.scene = scene

        # Get data
        json_data = self.list_item.data(QLVarsListWidget.JSON_DATA_ROLE)
        self.var_name = json_data['var_name']
        self.setTitle('Varible: {0}'.format(self.var_name))

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        var_data_type_name = self.scene.vars.get_data_type(self.var_name, as_dict=False)
        var_data_type = self.scene.vars.get_data_type(self.var_name, as_dict=True)
        var_value = self.scene.vars.get_value(self.var_name)

        # Widget creation
        self.data_type_box = QtWidgets.QComboBox()
        types_list = list(editor_conf.DATATYPE_REGISTER.keys())  # type: list
        types_list.sort()
        types_list.remove('EXEC')

        self.data_type_box.addItems(types_list)
        self.data_type_box.setCurrentText(var_data_type_name)

        self.value_widget = None
        if var_data_type['class'] in editor_conf.DataType.runtime_types(classes=True):
            self.value_widget = QtWidgets.QLineEdit()
            self.value_widget.setText(str(var_value))
            self.value_widget.setEnabled(False)
        elif var_data_type == editor_conf.DataType.NUMERIC:
            self.value_widget = QtWidgets.QDoubleSpinBox()
            self.value_widget.setRange(-9999, 9999)
            self.value_widget.setValue(var_value)
        elif var_data_type == editor_conf.DataType.STRING:
            self.value_widget = QtWidgets.QLineEdit()
            self.value_widget.setText(var_value)
        elif var_data_type == editor_conf.DataType.BOOLEAN:
            self.value_widget = QtWidgets.QCheckBox()
            self.value_widget.setChecked(var_value)
        else:
            Logger.debug('Missing widget creation for data {0}'.format(var_data_type['class']))

    def create_layouts(self):
        self.main_layout = QtWidgets.QFormLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addRow('Type:', self.data_type_box)
        if self.value_widget:
            self.main_layout.addRow('Value:', self.value_widget)

    def create_connections(self):
        self.data_type_box.currentTextChanged.connect(lambda typ_name: self.scene.vars.set_data_type(self.var_name, typ_name))
        self.data_type_box.currentTextChanged.connect(self.on_data_type_switched)

        if self.value_widget:
            if isinstance(self.value_widget, QtWidgets.QLineEdit):
                self.value_widget.textChanged.connect(lambda text: self.scene.vars.set_value(self.var_name, text))
            elif isinstance(self.value_widget, QtWidgets.QAbstractSpinBox):
                self.value_widget.valueChanged.connect(lambda value: self.scene.vars.set_value(self.var_name, value))
            elif isinstance(self.value_widget, QtWidgets.QCheckBox):
                self.value_widget.toggled.connect(lambda state: self.scene.vars.set_value(self.var_name, state))

    def on_data_type_switched(self):
        self.data_type_switched.emit(self.list_item, self.var_name)
