import pymel.core as pm
from Luna import Logger
try:
    from Luna.interface import buildManager
    from Luna.interface import configManager
except Exception as e:
    Logger.exception("Failed to import modules", exc_info=e)


def build_manager(*args):
    buildManager.MainDialog.display()


def prefs_manager(*args):
    configManager.MainDialog.display()
