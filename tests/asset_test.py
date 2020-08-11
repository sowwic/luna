from Luna.workspace import asset
from Luna.workspace import project
from Luna.core.config import Config
from Luna.core.config import ProjectVars
from PySide2 import QtWidgets
reload(project)
reload(asset)

prev_path = Config.get(ProjectVars.previous_project, "")
path = QtWidgets.QFileDialog.getExistingDirectory(None, "Set Luna project", prev_path)
if path:
    test_project = project.Project.set(path)
    test_asset = asset.Asset(name="testAsset", typ="character")
