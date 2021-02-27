import os
import pymel.api as pma
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from luna.static import directories
from shiboken2 import wrapInstance


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
    return wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)


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
