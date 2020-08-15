import os
import platform
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
        config_dir = Config.get_config_dir()
        config_file = os.path.join(config_dir, "Luna_config.json")
        if not os.path.isfile(config_file):
            shutil.copy2(Directories.LUNA_DEFAULT_CONFIG_PATH, config_file)
            Logger.info("Luna config reset to default")

    @staticmethod
    def get_config_dir():
        if platform.system() == "Darwin":
            config_dir = os.path.join(os.path.expanduser("~/Library/Preferences"), "Luna")
        elif platform.system() == "Windows":
            config_dir = os.path.join(os.getenv("LOCALAPPDATA"), "Luna")
        fileFn.create_missing_dir(config_dir)

        return config_dir

    @ staticmethod
    def get_config_file():
        config_dir = Config.get_config_dir()
        config_file = os.path.join(config_dir, "Luna_config.json")
        if not os.path.isfile(config_file):
            shutil.copy2(Directories.LUNA_DEFAULT_CONFIG_PATH, config_file)
            Logger.debug("Default config copied to: {0}".format(config_file))

        return config_file


if __name__ == "__main__":
    pass
