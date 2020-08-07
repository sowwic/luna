from Luna.core import asset
from Luna.core import workspace
from Luna.core import optionVarFn
from PySide2 import QtWidgets
reload(workspace)
reload(asset)

prevPath = optionVarFn.getOptionVar(optionVarFn.LunaVars.previous_workspace.value, default="")
path = QtWidgets.QFileDialog.getExistingDirectory(None, "Set Luna workspace", prevPath)
if path:
    test_workspace = workspace.Workspace.set(path)
    test_asset = asset.Asset(name="testAsset", typ="character")
