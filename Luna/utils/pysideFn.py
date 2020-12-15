import os
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from Luna.static import directories


def save_pixmap(path, pixmap, quality=-1):
    img_file = QtCore.QFile(path)
    img_file.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(img_file, "JPG", quality=quality)
    img_file.close()


def get_QIcon(name, maya_icon=False):
    if maya_icon:
        return QtGui.QIcon(":" + name)
    return QtGui.QIcon(os.path.join(directories.ICONS_PATH, name))
