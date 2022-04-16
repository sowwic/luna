from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node
from luna_builder.editor.node_attrib_widget import AttribWidget


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self._code_editor = editor

    def sizeHint(self):
        return QtCore.QSize(self._code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._code_editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super(CodeEditor, self).__init__()
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged[int].connect(self.update_line_number_area_width)
        self.updateRequest[QtCore.QRect, int].connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        # Tab space
        self.setTabStopWidth(self.fontMetrics().width(" ") * 4)

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num *= 0.1
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def resizeEvent(self, e):
        super(CodeEditor, self).resizeEvent(e)
        cr = self.contentsRect()
        width = self.line_number_area_width()
        rect = QtCore.QRect(cr.left(), cr.top(), width, cr.height())
        self.line_number_area.setGeometry(rect)

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.line_number_area)
        painter.begin(self)
        painter.fillRect(event.rect(), QtCore.Qt.lightGray)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QtCore.Qt.black)
                width = self.line_number_area.width()
                height = self.fontMetrics().height()
                painter.drawText(0, top, width, height, QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
        painter.end()

    def update_line_number_area_width(self, newBlockCount):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            width = self.line_number_area.width()
            self.line_number_area.update(0, rect.y(), width, rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)

            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()

            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)


class ScriptAttribWidget(AttribWidget):
    def init_fields(self):
        super(ScriptAttribWidget, self).init_fields()
        self.code_editor = CodeEditor()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.code_editor)

    def update_fields(self):
        super(ScriptAttribWidget, self).update_fields()
        self.code_editor.setPlainText(self.node.code)

    def create_signal_connections(self):
        super(ScriptAttribWidget, self).create_signal_connections()
        self.code_editor.textChanged.connect(
            lambda: self.node.set_code(self.code_editor.toPlainText()))


class ScriptNode(luna_node.LunaNode):
    ATTRIB_WIDGET = ScriptAttribWidget

    ID = 6
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    TITLE_EDITABLE = True
    ICON = 'python.png'
    DEFAULT_TITLE = 'Script'
    PALETTE_LABEL = 'Script (Python)'
    CATEGORY = 'Utils'

    def __init__(self, scene, title=None):
        super(ScriptNode, self).__init__(scene, title=title)
        self.code = ""

    def execute(self):
        exec(self.code)

    def set_code(self, value):
        self.code = value

    def serialize(self):
        res = super(ScriptNode, self).serialize()
        res["code"] = self.code
        return res

    def deserialize(self, data, hashmap, restore_id=True):
        super(ScriptNode, self).deserialize(data, hashmap, restore_id)  # type: ScriptNode
        self.code = data.get("code", "")


def register_plugin():
    editor_conf.register_node(ScriptNode.ID, ScriptNode)
