from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from Luna import Logger


def save_pixmap(path, pixmap, quality=-1):
    img_file = QtCore.QFile(path)
    img_file.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(img_file, "JPG", quality=quality)
    img_file.close()
