from os import environ
from Luna.core.loggingFn import Logger


def set_workspace_var(value):
    environ.data["LUNA_WORKSPACE"] = value
    Logger.debug("LUNA_WORKSPACE: {0}".format(value))


def get_workspace_var():
    """Get workpace object stored in enviroment variable

    :return: Current workspace
    :rtype: Luna.core.workspace.Workspace
    """
    return environ.get("LUNA_WORKSPACE")


def set_asset_var(value):
    environ.data["LUNA_ASSET"] = value
    Logger.debug("LUNA_ASSET: {0}".format(value))


def get_asset_var():
    return environ.get("LUNA_ASSET")


def set_character_var(value):
    environ.data["LUNA_CHARACTER"] = value
    Logger.debug("LUNA_CHARACTER: {0}".format(value))


def get_character_var():
    return environ.get("LUNA_CHARACTER")
