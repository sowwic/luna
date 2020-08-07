from Luna.core import asset
from Luna.core import workspace
from Luna.core.configFn import LunaConfig
from Luna.core.configFn import WorkspaceVars
from PySide2 import QtWidgets
reload(workspace)
reload(asset)

prevPath = LunaConfig.get(WorkspaceVars.previousWorkspace, "")
path = QtWidgets.QFileDialog.getExistingDirectory(None, "Set Luna workspace", prevPath)
if path:
    test_workspace = workspace.Workspace.set(path)
    test_asset = asset.Asset(name="testAsset", typ="character")
