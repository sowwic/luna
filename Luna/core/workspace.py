import os
import pymel.core as pm
from datetime import datetime

from Luna.core.loggingFn import Logger
try:
    from Luna.utils import fileFn
    from Luna.utils import environFn
    from Luna.core import optionVarFn
    from Luna.interface.hud import LunaHud
except Exception:
    Logger.exception("Failed to import modules")


class Workspace:
    """
    Base workspace class. Represents rigging workspace/project.
    """
    TAG_FILE = "workspace.proj"

    def __init__(self, path):
        self.path = path  # type: str
        self.name = os.path.basename(path)  # type:str
        self.meta_path = os.path.join(self.path, self.name + ".meta")  # type:str
        self.tag_path = os.path.join(self.path, self.TAG_FILE)  # type:str

    @classmethod
    def is_workspace(cls, path):
        search_file = os.path.join(path, cls.TAG_FILE)
        Logger.debug("Workpace check ({0}) - {1}".format(os.path.isfile(search_file), path))
        return os.path.isfile(search_file)

    def get_meta(self):
        meta_dict = {}
        if os.path.isfile(self.meta_path):
            meta_dict = fileFn.load_json(self.meta_path)

        for category in os.listdir(self.path):
            category_path = os.path.join(self.path, category)
            if os.path.isdir(category_path):
                asset_dirs = filter(os.path.isdir, [os.path.join(category_path, item) for item in os.listdir(category_path)])
                meta_dict[category] = [os.path.basename(asset) for asset in asset_dirs]
        Logger.debug("{0} meta: {1}".format(self.name, meta_dict))
        return meta_dict

    @ staticmethod
    def create(path):
        if Workspace.is_workspace(path):
            Logger.error("Already a workspace: {0}".format(path))
            return

        new_workspace = Workspace(path)
        # Create missing meta and tag files
        fileFn.create_missing_dir(new_workspace.path)
        fileFn.create_file(path=new_workspace.tag_path)
        meta_data = new_workspace.get_meta()
        creation_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        meta_data["created"] = creation_date
        fileFn.write_json(new_workspace.meta_path, data=meta_data)

        # Set enviroment variables and refresh HUD
        environFn.set_workspace_var(new_workspace)
        pm.optionVar[optionVarFn.LunaVars.previous_workspace.value] = new_workspace.path
        LunaHud.refresh()

        Logger.debug("New workspace path: {0}".format(new_workspace.path))
        Logger.debug("New workspace name: {0}".format(new_workspace.name))
        Logger.debug("Prev workspace optionVar: {0}".format(pm.optionVar[optionVarFn.LunaVars.previous_workspace.value]))

        return new_workspace

    @staticmethod
    def set(path):
        if not Workspace.is_workspace(path):
            Logger.error("Not a workspace: {0}".format(path))

        workspace_instance = Workspace(path)
        meta_data = workspace_instance.get_meta()
        fileFn.write_json(workspace_instance.meta_path, data=meta_data)

        # Set enviroment variables and refresh HUD
        environFn.set_workspace_var(workspace_instance)
        pm.optionVar[optionVarFn.LunaVars.previous_workspace.value] = workspace_instance.path
        LunaHud.refresh()

        Logger.debug("Set workspace path: {0}".format(workspace_instance.path))
        Logger.debug("Set workspace name: {0}".format(workspace_instance.name))
        Logger.debug("Prev workspace optionVar: {0}".format(pm.optionVar[optionVarFn.LunaVars.previous_workspace.value]))

        return workspace_instance

    @staticmethod
    def exit():
        environFn.set_asset_var(None)
        environFn.set_workspace_var(None)
        environFn.set_character_var(None)
        LunaHud.refresh()
