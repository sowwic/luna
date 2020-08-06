import json
import pymel.core as pm
from Luna.utils.enumFn import Enum
from Luna.core.loggingFn import Logger


class LunaVars(Enum):
    """ Luna vars"""
    previous_workspace = "LunaPrevWorkspace"
    recent_workspaces = "LunaRecentWorkspaces"


class ToolVars(Enum):
    locator_tool = "LunaLocatorToolOptions"


def getOptionVar(var, default="", as_dict=False):
    if isinstance(default, dict):
        default = json.dumps(default)

    value = pm.optionVar.get(var, default)
    Logger.debug("Var: {0} Value: {1}".format(var, value))
    if as_dict:
        value = json.loads(value)

    return value


def toggleOptionVar(var):
    if var in pm.optionVar:
        value = pm.optionVar[var]
        if value == 0:
            value = 1
        elif value == 1:
            value = 0
        pm.optionVar[var] = value
