from os import environ
from Luna import Logger


def set_project_var(value):
    environ.data["LUNA_PROJECT"] = value
    Logger.debug("LUNA_PROJECT: {0}".format(value))


def get_project_var():
    """Get workpace object stored in enviroment variable

    :return: Current project
    :rtype: Luna.workspace.project.Project
    """
    return environ.get("LUNA_PROJECT")


def set_asset_var(value):
    environ.data["LUNA_ASSET"] = value
    Logger.debug("LUNA_ASSET: {0}".format(value))


def get_asset_var():
    return environ.get("LUNA_ASSET")
