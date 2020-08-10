import webbrowser
import pymel.core as pm
from Luna import Logger
from Luna import __version__
from PySide2 import QtWidgets


def show_about_dialog(*args):
    QtWidgets.QMessageBox.about(None, "Luna", "version: {0}".format(__version__))


def open_docs(*args):
    Logger.debug("TODO: open Luna docs")
