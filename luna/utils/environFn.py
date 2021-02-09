import luna
from os import environ
from luna import Logger


def set_project_var(value):
    environ.data["LUNA_PROJECT"] = value
    Logger.debug("LUNA_PROJECT: {0}".format(value))


def get_project_var():
    """Get workpace object stored in enviroment variable

    :return: Current project
    :rtype: luna.workspace.Project
    """
    project = environ.get("LUNA_PROJECT")  # type: luna.workspace.Project
    return project


def set_asset_var(value):
    environ.data["LUNA_ASSET"] = value
    Logger.debug("LUNA_ASSET: {0}".format(value))


def get_asset_var():
    asset = environ.get("LUNA_ASSET")  # type: luna.workspace.Asset
    return asset


def set_character_var(value):
    environ.data["LUNA_CHARACTER"] = value
    Logger.debug("LUNA_CHARACTER : {0}".format(value))


def get_character_var():
    return environ.get("LUNA_CHARACTER")
