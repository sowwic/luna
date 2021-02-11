import pymel.core as pm
import os
import luna.utils.fileFn as fileFn


class UnrealProject(object):

    META_EXT = ".uproject"

    @classmethod
    def is_project(cls, path):
        if not os.path.isdir(path):
            return False
        project_files = [item.endswith(cls.META_EXT) for item in os.listdir(path)]
        return any(project_files)

    @property
    def content_dir(self):
        path = os.path.join(self.path, "Content")  # type: str
        return path

    def __init__(self, path):
        self.path = path
        self.name = None
        self.engine_version = None
        self.parse_meta()

    def parse_meta(self):
        meta_file = [item.endswith(self.META_EXT) for item in os.listdir(self.path)][0]  # type: str
        self.name = meta_file.split(self.META_EXT)[0]
        meta_data = fileFn.load_json(meta_file)
        self.engine_version = meta_data.get("EngineAssociation")
