from Luna import Logger
from Luna.utils import environFn

current_workspace = environFn.get_workspace_var()
Logger.debug("Current workspace path: {0}".format(current_workspace.path))
