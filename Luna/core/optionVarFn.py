import json
import pymel.core as pm
from Luna.utils.enumFn import Enum
from Luna.core.loggingFn import Logger


class OptionVars(Enum):
    """ Luna vars"""
    previous_workspace = "LunaPrevWorkspace"
    recent_workspaces = "LunaRecentWorkspaces"


class ToolVars(Enum):
    locator_tool = "LunaLocatorToolOptions"


def getOptionVar(var, default="", asDict=False):
    if var not in pm.optionVar and default:
        # Convert to string if dictionary
        if isinstance(default, dict):
            default = json.dumps(default)
        pm.optionVar.setdefault(var, default)

    value = pm.optionVar[var]
    if asDict:
        value = json.loads(pm.optionVar[var])

    return value


def toggleOptionVar(var):
    if var in pm.optionVar:
        value = pm.optionVar[var]
        if value == 0:
            value = 1
        elif value == 1:
            value = 0
        pm.optionVar[var] = value
