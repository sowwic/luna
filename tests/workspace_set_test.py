from Luna.workspace import project
from Luna.core.configFn import LunaConfig
from Luna.core.configFn import ProjectVars
from PySide2 import QtWidgets
reload(project)

prevPath = LunaConfig.get(ProjectVars.previous_project, "")
path = QtWidgets.QFileDialog.getExistingDirectory(None, "Set Luna project", "")
if path:
    test_project = project.Project.set(path)
