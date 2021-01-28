import webbrowser
import pymel.core as pm
from luna import Logger
from luna import __version__
from PySide2 import QtWidgets
from PySide2 import QtGui
from luna.utils import fileFn


def show_about_dialog(*args):
    help_text = "luna\nVersion: {0}".format(__version__)
    icon_pixmap = QtGui.QPixmap(fileFn.get_icon_path("luna.png"))
    icon_pixmap = icon_pixmap.scaled(128, 128)
    about_dialog = QtWidgets.QMessageBox()
    about_dialog.setWindowIcon(QtGui.QIcon(icon_pixmap))
    about_dialog.setWindowTitle("luna")
    about_dialog.setText(help_text)
    about_dialog.setIconPixmap(icon_pixmap)
    about_dialog.exec_()


def open_docs(*args):
    Logger.debug("TODO: open luna docs")
