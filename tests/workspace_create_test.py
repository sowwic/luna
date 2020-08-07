from Luna.core import workspace
from Luna.core import optionVarFn
from PySide2 import QtWidgets
reload(workspace)

prevPath = optionVarFn.getOptionVar(optionVarFn.LunaVars.previous_workspace.value, default="")
path = QtWidgets.QFileDialog.getExistingDirectory(None, "Create Luna workspace", prevPath)
if path:
    test_workspace = workspace.Workspace.create(path)
