import pymel.core as pm
from Luna import Logger
try:
    from Luna.tools import buildManager
    from Luna.tools import configManager
except Exception as e:
    Logger.exception("Failed to import modules", exc_info=e)


def build_manager(*args):
    buildManager.MainDialog.display()


def config_manager(*args):
    configManager.MainDialog.display()
