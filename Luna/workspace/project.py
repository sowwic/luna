import os
from collections import deque
from datetime import datetime

from Luna import Logger
try:
    from Luna.utils import fileFn
    from Luna.utils import environFn
    from Luna import Config
    from Luna import ProjectVars
    from Luna.interface.hud import LunaHud
except Exception:
    Logger.exception("Failed to import modules")


class Project:
    """
    Base project class. Represents rigging project
    """
    TAG_FILE = "luna.proj"

    def __repr__(self):
        return "{0}({1}): {2}".format(self.name, self.path, self.get_meta())

    def __init__(self, path):
        self.path = path  # type: str
        self.name = os.path.basename(path)  # type:str
        self.meta_path = os.path.join(self.path, self.name + ".meta")  # type:str
        self.tag_path = os.path.join(self.path, self.TAG_FILE)  # type:str

    @classmethod
    def is_project(cls, path):
        search_file = os.path.join(path, cls.TAG_FILE)
        Logger.debug("isProject check ({0}) - {1}".format(os.path.isfile(search_file), path))
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
        return meta_dict

    def add_to_recent(self):
        max_recent = Config.get(ProjectVars.recent_max, default=3)
        project_queue = Config.get(ProjectVars.recent_projects, default=deque(maxlen=max_recent))
        if not isinstance(project_queue, deque):
            project_queue = deque(project_queue, maxlen=max_recent)

        entry = [self.name, self.path]
        if entry in project_queue:
            return

        project_queue.appendleft(entry)
        Config.set(ProjectVars.recent_projects, list(project_queue))

    def update_meta(self):
        meta_data = self.get_meta()
        fileFn.write_json(self.meta_path, data=meta_data)

    @ staticmethod
    def create(path):
        if Project.is_project(path):
            Logger.error("Already a project: {0}".format(path))
            return

        new_project = Project(path)
        # Create missing meta and tag files
        fileFn.create_missing_dir(new_project.path)
        fileFn.create_file(path=new_project.tag_path)
        meta_data = new_project.get_meta()
        creation_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        meta_data["created"] = creation_date
        fileFn.write_json(new_project.meta_path, data=meta_data)

        # Set enviroment variables and refresh HUD
        environFn.set_project_var(new_project)
        Config.set(ProjectVars.previous_project, new_project.path)
        new_project.add_to_recent()
        LunaHud.refresh()

        Logger.debug("New project: {0}".format(new_project))

        return new_project

    @ staticmethod
    def set(path):
        if not Project.is_project(path):
            Logger.error("Not a project: {0}".format(path))
            return

        project_instance = Project(path)
        meta_data = project_instance.get_meta()
        fileFn.write_json(project_instance.meta_path, data=meta_data)

        # Set enviroment variables and refresh HUD
        environFn.set_project_var(project_instance)
        Config.set(ProjectVars.previous_project, project_instance.path)
        project_instance.add_to_recent()
        LunaHud.refresh()

        Logger.debug("Setted project: {0}".format(project_instance))
        # Logger.debug("Set project path: {0}".format(project_instance.path))
        # Logger.debug("Set project name: {0}".format(project_instance.name))

        return project_instance

    @staticmethod
    def get():
        project_instance = environFn.get_project_var()  # type: Project
        return project_instance

    @ staticmethod
    def exit():
        environFn.set_asset_var(None)
        environFn.set_project_var(None)
        LunaHud.refresh()

    @staticmethod
    def refresh_recent():
        recent_projects = Config.get(ProjectVars.recent_projects)
        existing_projects = []
        for prj in recent_projects:
            if os.path.isdir(prj[1]):
                existing_projects.append(prj)
        Config.set(ProjectVars.recent_projects, existing_projects)
