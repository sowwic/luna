from Luna.core import workspace
from Luna.core.configFn import LunaConfig
from Luna.core.configFn import WorkspaceVars
from PySide2 import QtWidgets
reload(workspace)

prevPath = LunaConfig.get(WorkspaceVars.previousWorkspace, "")
path = QtWidgets.QFileDialog.getExistingDirectory(None, "Create Luna workspace", prevPath)
if path:
    test_workspace = workspace.Workspace.create(path)
