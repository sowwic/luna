"""Common file operations"""
import json
import os
import pickle
import shutil
import pymel.core as pm
from Luna import Logger
from Luna.static import Directories


# Json
def write_json(path, data={}, as_string=False, sort_keys=True):
    try:
        with open(path, "w") as json_file:
            if as_string:
                json_file.write(json.dumps(data, sort_keys=sort_keys, indent=4, separators=(",", ":")))
            else:
                json.dump(data, json_file, indent=4)

    except IOError as e:
        Logger.exception("{0} is not a valid file path".format(path), exc_info=e)
        return None

    except BaseException:
        Logger.exception("Failed to write file {0}".format(path), exc_info=1)
        return None

    return path


def load_json(path, string_data=False):
    try:
        with open(path, "r") as json_file:
            if string_data:
                data = json.loads(json_file)
            else:
                data = json.load(json_file)

    except IOError as e:
        Logger.exception("{0} is not a valid file path".format(path), exc_info=e)
        return None
    except BaseException:
        Logger.exception("Failed to load file {0}".format(path), exc_info=e)
        return None

    return data


# Pickle
def write_pickle(path, data):
    backup_data = {}
    status = 1

    backup_data = load_pickle(path)

    # Check if backup was saved
    if not status:
        return path, status

    try:
        with open(path, "w") as new_file:
            pickle.dump(data, new_file)
    except IOError:
        Logger.exception("Failed to saved file: {0}".format(path))
        pickle.dump(backup_data, new_file)
        Logger.warning("Reverted backup data for {0}".format(0))
        status = 0

    return path, status


def load_pickle(path):
    try:
        with open(path, "r") as read_file:
            data = pickle.load(read_file)
    except IOError as e:
        Logger.exception("Failed to load file {0}".format(path), exc_info=e)
        return None

    return data


# File
def create_file(path, data=""):
    try:
        with open(path, "w") as f:
            f.write(data)
    except IOError:
        Logger.exception("Failed to create file {0}".format(path))
        return None

    return path


def delete_oldest(directory, file_limit):
    all_files = ["{0}/{1}".format(directory, child) for child in os.listdir(directory)]

    if file_limit and len(all_files) > file_limit:
        try:
            oldest_file = min(all_files, key=os.path.getctime)
            os.remove(oldest_file)
            return oldest_file
        except Exception as e:
            Logger.exception("Failed to delete file {0}".format(oldest_file), exc_info=e)
            return None


# Directory
def create_missing_dir(path):
    """Creates specified directory if one doesn't exist

    :param path: Directory path
    :type path: str
    :return: Path to directory
    :rtype: str
    """
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


# Pipeline functions
def copy_empty_scene(new_path):
    if os.path.isfile(new_path):
        return

    source_path = os.path.join(Directories.EMPTY_SCENES_PATH, "EmptyScene_Maya{0}.ma".format(pm.about(v=1)))
    Logger.debug("Copying file {0} to {1}".format(source_path, new_path))
    if not os.path.isfile(source_path):
        raise IOError
    try:
        shutil.copy2(source_path, new_path)
    except Exception:
        Logger.exception("Failed to copy scene {0}".format(source_path))


def get_icon(name):
    return os.path.join(Directories.ICONS_PATH, name)


if __name__ == "__main__":
    pass
