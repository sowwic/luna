from Luna import Logger
from Luna.utils import environFn

current_project = environFn.get_project_var()
Logger.debug("Current project path: {0}".format(current_project.path))
