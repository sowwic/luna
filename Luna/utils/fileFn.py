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

    return data  # type:dict


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


def get_versioned_files(path, extension="", split_char="."):
    files_dict = {}
    all_files = [item for item in os.listdir(path) if os.path.isfile(os.path.join(path, item))]
    if extension:
        all_files = [item for item in all_files if item.endswith("." + extension)]

    # Fill dict
    for each_file in all_files:
        if each_file.split(split_char)[0] not in files_dict.keys():
            files_dict[each_file.split(split_char)[0]] = [each_file]
        else:
            files_dict[each_file.split(split_char)[0]].append(each_file)

    # Sort items for each key
    for key, value in files_dict.iteritems():
        files_dict[key] = sorted(value)

    return files_dict


def get_latest_file(name, dir_path, extension="", full_path=False, split_char="."):
    files_dict = get_versioned_files(dir_path, extension, split_char)
    if name not in files_dict.keys():
        return None
    if full_path:
        return os.path.join(dir_path, files_dict.get(name)[-1])
    else:
        return files_dict.get(name)[-1]


def get_new_versioned_file(name, dir_path, extension="", split_char=".", full_path=False):
    files_dict = get_versioned_files(dir_path, extension, split_char)
    if name in files_dict.keys():
        new_version = int(files_dict.get(name)[-1].split(split_char)[-2]) + 1
    else:
        new_version = 0

    new_file_name = "{0}.{1}.{2}".format(name, str(new_version).zfill(4), extension)
    if full_path:
        return os.path.join(dir_path, new_file_name)

    return "{0}.{1}.{2}".format(name, str(new_version).zfill(4), extension)
