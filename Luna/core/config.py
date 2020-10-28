import os
import shutil
from Luna import Logger
from Luna.utils import fileFn
from Luna.static import Directories


class ProjectVars:
    recent_projects = "project.recent"
    previous_project = "project.previous"


class LunaVars:
    logging_level = "logging.level"
    command_port = "python.commandPort"


class HudVars:
    block = "hud.block"
    section = "hud.section"


class Config:
    @classmethod
    def load(cls):
        return fileFn.load_json(cls.get_config_file())

    @classmethod
    def update(cls, new_config_dict):
        current_config = cls.load()  # type: dict
        current_config.update(new_config_dict)
        fileFn.write_json(cls.get_config_file(), current_config)

    @classmethod
    def get(cls, key, default=None):
        current_config = cls.load()  # type:dict
        if key not in current_config.keys():
            current_config[key] = default
            cls.update(current_config)
        return current_config.get(key)

    @classmethod
    def set(cls, key, value):
        cls.update({key: value})

    @classmethod
    def reset(cls):
        shutil.copy2(Directories.DEFAULT_CONFIG_PATH, Directories.CONFIG_PATH)
        Logger.info("Luna config reset to default")

    @ staticmethod
    def get_config_file():
        if not os.path.isfile(Directories.CONFIG_PATH):
            shutil.copy2(Directories.DEFAULT_CONFIG_PATH, Directories.CONFIG_PATH)
            Logger.debug("Default config copied to: {0}".format(Directories.CONFIG_PATH))

        return Directories.CONFIG_PATH


if __name__ == "__main__":
    pass
