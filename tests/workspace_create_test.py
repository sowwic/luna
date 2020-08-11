from Luna.workspace import project
from Luna.core.config import Config
from Luna.core.config import ProjectVars
from PySide2 import QtWidgets
reload(project)

prev_path = Config.get(ProjectVars.previous_project, "")
path = QtWidgets.QFileDialog.getExistingDirectory(None, "Create Luna project", prev_path)
if path:
    test_project = project.Project.create(path)
