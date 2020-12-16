from PySide2 import QtWidgets
from PySide2 import QtGui
from Luna import Logger
from Luna.utils import enumFn


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

    def resizeEvent(self, e):
        self.scroll_area.resizeEvent(e)
