import logging
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


LOGGER = logging.getLogger(__name__)


def savePixMap(filePath, pixmap, quality=-1):
    imgFile = QtCore.QFile(filePath)
    imgFile.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(imgFile, "JPG", quality=quality)
    imgFile.close()
