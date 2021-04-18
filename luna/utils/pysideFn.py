import os
import pymel.core as pm
import pymel.api as pma
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from luna.static import directories
from shiboken2 import wrapInstance
from shiboken2 import getCppPointer


def save_pixmap(path, pixmap, quality=-1):
    img_file = QtCore.QFile(path)
    img_file.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(img_file, "JPG", quality=quality)
    img_file.close()


def get_QIcon(name, maya_icon=False):
    if maya_icon:
        return QtGui.QIcon(":" + name)
    return QtGui.QIcon(os.path.join(directories.ICONS_PATH, name))


def maya_main_window():
    mainWindowPtr = pma.MQtUtil_mainWindow()
    if os.sys.version_info[0] >= 3:
        return wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)


def add_widget_to_layout(widget, control_name):
    if pm.workspaceControl(control_name, q=1, ex=1):
        workspaceControlPtr = long(pma.MQtUtil.findControl(control_name))
        if os.sys.version_info[0] >= 3:
            widgetPtr = int(getCppPointer(widget)[0])
        else:
            widgetPtr = long(getCppPointer(widget)[0])

        pma.MQtUtil.addWidgetToMayaLayout(widgetPtr, workspaceControlPtr)


def qlist_all_items(qlist):
    if not isinstance(qlist, QtWidgets.QListWidget):
        raise TypeError("Invalid widget type. Must be QListWidget")
    items = []
    for index in range(qlist.count()):
        items.append(qlist.item(index))
    return items


def line_separator():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


class ReValidators:
    no_space = QtGui.QRegExpValidator(QtCore.QRegExp("^[A-Za-z0-9]+"))
