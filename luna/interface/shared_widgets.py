from maya.app.general import resourceBrowser
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
import luna_rig
import luna_rig.functions.animFn as animFn
from luna import Logger
import luna.utils.enumFn as enumFn
import luna.utils.inspectFn as inspectFn
reload(inspectFn)


class PathWidget(QtWidgets.QWidget):

    class Mode(enumFn.Enum):
        EXISTING_DIR = 0
        EXISTING_FILE = 1
        SAVE_FILE = 2

    def __init__(self, parent=None, mode=Mode.EXISTING_DIR, default_path="", label_text="", dialog_label=""):
        super(PathWidget, self).__init__(parent)
        self.mode = mode.value if isinstance(mode, PathWidget.Mode) else mode
        self.default_path = default_path
        self.label_text = label_text
        self.dialog_label = dialog_label

        self._create_widgets()
        self._create_layouts()
        self._create_connections()

    def _create_widgets(self):
        self.label = QtWidgets.QLabel(self.label_text)
        self.line_edit = QtWidgets.QLineEdit(self.default_path)
        self.browse_button = QtWidgets.QPushButton()
        self.browse_button.setIcon(QtGui.QIcon(":fileOpen.png"))

    def _create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.line_edit)
        self.main_layout.addWidget(self.browse_button)

    def _create_connections(self):
        self.browse_button.clicked.connect(self.get_path)

    def get_path(self):
        if self.mode == 0:
            self._get_existing_dir()
        elif self.mode == 1:
            self._get_existing_file()
        elif self.mode == 2:
            self._get_save_file()

    def _get_save_file(self):
        if not self.dialog_label:
            self.dialog_label = "Select save file"
        path = QtWidgets.QFileDialog.getSaveFileName(None, self.dialog_label, self.line_edit.text())
        if path:
            self.line_edit.setText(path)

    def _get_existing_file(self):
        if not self.dialog_label:
            self.dialog_label = "Select existing file"
        path, extra = QtWidgets.QFileDialog.getOpenFileName(None, self.dialog_label, self.line_edit.text())
        if path:
            self.line_edit.setText(path)

    def _get_existing_dir(self):
        if not self.dialog_label:
            self.dialog_label = "Set directory"
        path = QtWidgets.QFileDialog.getExistingDirectory(None, self.dialog_label, self.line_edit.text())
        if path:
            self.line_edit.setText(path)

    def add_widget(self, widget):
        self.main_layout.addWidget(widget)


class ScrollWidget(QtWidgets.QWidget):
    def __init__(self, border=0, **kwargs):
        super(ScrollWidget, self).__init__(**kwargs)

        self.content = QtWidgets.QWidget(self)
        self.scroll_area = QtWidgets.QScrollArea()

        self.scroll_area.setWidget(self.content)
        self.scroll_area.setWidgetResizable(1)

        self.content_layout = QtWidgets.QVBoxLayout()
        self.content.setLayout(self.content_layout)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.scroll_area)
        self.layout().setContentsMargins(0, 0, 0, 0)

        if not border:
            self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        self.content_layout.addLayout(layout)

    def resizeEvent(self, e):
        self.scroll_area.resizeEvent(e)


class LineFieldWidget(QtWidgets.QWidget):
    def __init__(self, label_text, button_text, parent=None):
        super(LineFieldWidget, self).__init__(parent)
        self.label = QtWidgets.QLabel(label_text)
        self.button = QtWidgets.QPushButton(button_text)
        self.line_edit = QtWidgets.QLineEdit()
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.line_edit)
        self.main_layout.addWidget(self.button)
        self.setLayout(self.main_layout)


class TimeRangeWidget(QtWidgets.QGroupBox):
    def __init__(self, parent=None, title="Time", mode=0, start_time=0, end_time=120, max_time=9999, min_time=-9999):
        super(TimeRangeWidget, self).__init__(title, parent)

        # Widgets
        self.timeslider_radio = QtWidgets.QRadioButton("Time slider")
        self.startend_radio = QtWidgets.QRadioButton("Start/end")
        self.timeslider_radio.setChecked(mode)
        self.startend_radio.setChecked(not mode)

        self.start_label = QtWidgets.QLabel("Start:")
        self.start_time = QtWidgets.QSpinBox()
        self.start_time.setMinimumWidth(50)
        self.start_time.setMinimum(min_time)
        self.start_time.setMaximum(max_time)
        self.start_time.setValue(start_time)
        self.start_time.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.end_label = QtWidgets.QLabel("End:")
        self.end_time = QtWidgets.QSpinBox()
        self.end_time.setMinimumWidth(50)
        self.end_time.setMinimum(min_time)
        self.end_time.setMaximum(max_time)
        self.end_time.setValue(end_time)
        self.end_time.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

        # Layouts
        self.radio_layout = QtWidgets.QHBoxLayout()
        self.radio_layout.addWidget(QtWidgets.QLabel("Range:"))
        self.radio_layout.addWidget(self.timeslider_radio)
        self.radio_layout.addWidget(self.startend_radio)
        self.radio_layout.addStretch()
        self.time_range_layout = QtWidgets.QHBoxLayout()
        self.time_range_layout.addWidget(self.start_label)
        self.time_range_layout.addWidget(self.start_time)
        self.time_range_layout.addWidget(self.end_label)
        self.time_range_layout.addWidget(self.end_time)
        self.time_range_layout.addStretch()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.radio_layout)
        self.main_layout.addLayout(self.time_range_layout)
        self.setLayout(self.main_layout)

        # Connections
        self.startend_radio.toggled.connect(self.set_spinboxes_enabled)

    def showEvent(self, event):
        super(TimeRangeWidget, self).showEvent(event)
        self.set_spinboxes_enabled(self.startend_radio.isChecked())

    def set_spinboxes_enabled(self, state):
        for wgt in [self.start_label, self.start_time, self.end_label, self.end_time]:
            wgt.setEnabled(state)

    def get_range(self):
        if self.startend_radio.isChecked():
            return self.start_time.value(), self.end_time.value()
        else:
            return animFn.get_playback_range()


class ComponentsList(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ComponentsList, self).__init__(parent)

        self._create_widgets()
        self._create_layouts()
        self._create_connections()
        self.update_types()

    def showEvent(self, event):
        super(ComponentsList, self).showEvent(event)
        self.update_types()

    def _create_widgets(self):
        self.existing_checkbox = QtWidgets.QCheckBox("Only existing")
        self.existing_checkbox.setChecked(True)
        self.type_field = QtWidgets.QComboBox()
        self.type_field.setEditable(True)
        self.list = QtWidgets.QListWidget()
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def _create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.existing_checkbox)
        self.main_layout.addWidget(self.type_field)
        self.main_layout.addWidget(self.list)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def _create_connections(self):
        self.type_field.currentTextChanged.connect(self.update_items)
        self.existing_checkbox.toggled.connect(self.update_types)

    def get_selected_components(self):
        components = [item.data(1) for item in self.list.selectedItems() if isinstance(item.data(1), luna_rig.MetaNode)]
        return components

    def update_items(self):
        self.list.clear()
        for component in luna_rig.MetaNode.list_nodes(of_type=self.type_field.currentData()):
            list_item = QtWidgets.QListWidgetItem(str(component))
            list_item.setData(1, component)
            self.list.addItem(list_item)

    def update_types(self):
        self.type_field.clear()
        if self.existing_checkbox.isChecked():
            for meta_type, instances in luna_rig.MetaNode.get_existing_nodes().items():
                self.type_field.addItem(meta_type.as_str(name_only=True), meta_type)
        else:
            for cls_name, cls_ref in inspectFn.get_classes(luna_rig.components):
                self.type_field.addItem(cls_name, cls_ref)
            base_classes = inspectFn.get_classes(luna_rig, as_dict=True)
            self.type_field.addItem("AnimComponent", base_classes.get("AnimComponent"))


class ControlsList(QtWidgets.QWidget):
    def __init__(self, components_list, parent=None):
        super(ControlsList, self).__init__(parent)
        if not isinstance(components_list, ComponentsList):
            Logger.exception("Control list requires {0} instance.".format(ComponentsList))
            raise TypeError
        self.components_list = components_list  # type: ComponentsList
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.list = QtWidgets.QListWidget()
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.list)

    def create_connections(self):
        self.components_list.list.currentItemChanged.connect(self.update_list)

    def update_list(self, item):
        self.list.clear()
        if not item:
            return
        component = item.data(1)
        if not isinstance(component, luna_rig.AnimComponent) and not isinstance(component, luna_rig.components.Character):
            return
        for control in component.controls:
            list_item = QtWidgets.QListWidgetItem(control.transform.name())
            list_item.setData(1, control)
            self.list.addItem(list_item)


class FrameLayout(QtWidgets.QWidget):
    """dsFrameLayout class """

    def __init__(self, parent=None, title="", collapsed=True):
        super(FrameLayout, self).__init__(parent=parent)

        self._isCollapsed = collapsed
        self._titleFrame = None
        self._content = None
        self._contentLayout = None

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(self._init_titleFrame(title, self._isCollapsed))
        self.mainLayout.addWidget(self._init_content(self._isCollapsed))
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self._init_collapsable()

    def _init_titleFrame(self, title, collapsed):
        self._titleFrame = self.TitleFrame(title=title, collapsed=collapsed)

        return self._titleFrame

    def _init_content(self, collapsed):
        self._content = QtWidgets.QWidget()
        self._contentLayout = QtWidgets.QVBoxLayout()

        self._content.setLayout(self._contentLayout)
        self._content.setVisible(not collapsed)

        return self._content

    def _init_collapsable(self):
        self._titleFrame.clicked.connect(self.toggleCollapsed)

    def toggleCollapsed(self):
        self._content.setVisible(self._isCollapsed)
        self._isCollapsed = not self._isCollapsed
        self._titleFrame._arrow.setArrow(int(self._isCollapsed))

    def add_widget(self, widget):
        self._contentLayout.addWidget(widget)

    def add_layout(self, layout):
        self._contentLayout.addLayout(layout)

    class TitleFrame(QtWidgets.QFrame):
        clicked = QtCore.Signal()

        def __init__(self, parent=None, title="", collapsed=False):
            super(FrameLayout.TitleFrame, self).__init__(parent=parent)

            self.setMinimumHeight(24)
            self.move(QtCore.QPoint(24, 0))
            self.setStyleSheet("border:1px solid rgb(41, 41, 41);")
            self._hlayout = QtWidgets.QHBoxLayout(self)
            self._hlayout.setContentsMargins(10, 0, 0, 0)
            self._hlayout.setSpacing(0)
            self._arrow = None
            self._title = None
            self._hlayout.addWidget(self._init_arrow(collapsed))
            self._hlayout.addWidget(self._init_title(title))

        def _init_arrow(self, collapsed):
            self._arrow = FrameLayout.Arrow(collapsed=collapsed)
            self._arrow.setStyleSheet("border:0px")
            return self._arrow

        def _init_title(self, title=None):
            self._title = QtWidgets.QLabel(title)
            self._title.setMinimumHeight(24)
            self._title.move(QtCore.QPoint(24, 0))
            self._title.setStyleSheet("border:0px")
            return self._title

        def mousePressEvent(self, event):
            self.clicked.emit()
            return super(FrameLayout.TitleFrame, self).mousePressEvent(event)

    class Arrow(QtWidgets.QLabel):
        def __init__(self, parent=None, collapsed=False):
            super(FrameLayout.Arrow, self).__init__(parent=parent)
            self.setMaximumSize(18, 24)
            # horizontal == 0
            self._arrowHorizontal = QtGui.QPixmap(":arrowRight.png")
            # vertical == 1
            self._arrowVertical = QtGui.QPixmap(":arrowDown.png")
            self._arrow = None
            self.setArrow(int(collapsed))

        def setArrow(self, arrowDir):
            if arrowDir:
                self._arrow = self._arrowHorizontal
            else:
                self._arrow = self._arrowVertical
            self.setPixmap(self._arrow)
