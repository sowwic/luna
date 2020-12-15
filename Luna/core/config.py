import os
import shutil
from Luna import Logger
from Luna.utils import fileFn
from Luna.static import directories


class Config:
    DEFAULT_CONFIG_PATH = directories.DEFAULT_CONFIG_PATH
    FILE_PATH = directories.CONFIG_PATH

    @classmethod
    def load(cls):
        """Load config as dict

        Returns:
            dict: Config dictionary
        """
        return fileFn.load_json(cls.get_config_path())

    @classmethod
    def update(cls, new_config_dict):
        current_config = cls.load()  # type: dict
        current_config.update(new_config_dict)
        fileFn.write_json(cls.get_config_path(), current_config, sort_keys=False)

    @classmethod
    def get(cls, key, default=None):
        """Get setting by key

        Args:
            key (str): Setting name
            default (any, optional): Default value to set if key doesn't exist. Defaults to None.

        Returns:
            any: Value for requested setting
        """
        current_config = cls.load()  # type:dict
        if key not in current_config.keys():
            current_config[key] = default
            cls.update(current_config)
        return current_config.get(key)

    @classmethod
    def set(cls, key, value):
        """Sets setting to passed value

        Args:
            key (str): Setting name
            value (any): Value to set
        """
        cls.update({key: value})

    @classmethod
    def reset(cls):
        """
        Reset config to default. Copies default config file with normal config name
        """
        shutil.copy2(directories.DEFAULT_CONFIG_PATH, directories.CONFIG_PATH)
        Logger.info("Luna config reset to default")

    @ classmethod
    def get_config_path(cls):
        """Get path to config file. Copy a default one if one doesn't exist.

        Returns:
            str: Path to config file
        """
        if not os.path.isfile(cls.FILE_PATH):
            shutil.copy2(cls.DEFAULT_CONFIG_PATH, cls.FILE_PATH)
            Logger.debug("Default config copied to: {0}".format(cls.FILE_PATH))

        return cls.FILE_PATH


if __name__ == "__main__":
    pass
