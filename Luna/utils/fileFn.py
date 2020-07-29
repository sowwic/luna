"""Common file operations"""

import logging
import json
import os
import pickle

LOGGER = logging.getLogger(__name__)


# Json
def write_json(path, data={}, as_string=False, sort_keys=True):
    try:
        with open(path, "w") as json_file:
            if as_string:
                json_file.write(json.dumps(data, sort_keys=sort_keys, indent=4, separators=(",", ":")))
            else:
                json.dump(data, json_file, indent=4)

    except IOError as e:
        LOGGER.exception("{0} is not a valid file path".format(path), exc_info=e)
        return None

    except BaseException:
        LOGGER.exception("Failed to write file {0}".format(path), exc_info=1)
        return None

    return path


def load_json(path, as_string=False):
    try:
        with open(path, "r") as json_file:
            if as_string:
                data = json.loads(json_file)
            else:
                data = json.load(json_file)

    except IOError as e:
        LOGGER.exception("{0} is not a valid file path".format(path), exc_info=e)
        return None
    except BaseException:
        LOGGER.exception("Failed to load file {0}".format(path), exc_info=e)
        return None

    return data


# Pickle
def write_pickle(path, data):
    backupData = {}
    status = 1

    backupData = load_pickle(path)

    # Check if backup was saved
    if not status:
        return path, status

    try:
        with open(path, "w") as newFile:
            pickle.dump(data, newFile)
    except BaseException:
        LOGGER.error("Failed to saved file: {0}".format(path), exc_info=1)
        pickle.dump(backupData, newFile)
        LOGGER.warning("Reverted backup data for {0}".format(0))
        status = 0

    return path, status


def load_pickle(path):
    try:
        with open(path, "r") as readFile:
            data = pickle.load(readFile)
    except IOError as e:
        LOGGER.exception("Failed to load file {0}".format(path), exc_info=e)
        return None

    return data


# File
def create_file(directory, name, data="", extension="txt"):
    fileName = "{0}.{1}".format(name, extension)
    filePath = os.path.normpath(os.path.join(directory, fileName))
    try:
        with open(filePath, "w") as f:
            f.write(data)
    except IOError:
        LOGGER.exception("Failed to create file {0}".format(filePath))
        return None

    return (filePath, fileName)


def delete_oldest(directory, fileLimit):
    allFilePaths = ["{0}/{1}".format(directory, child) for child in os.listdir(directory)]

    if fileLimit and len(allFilePaths) > fileLimit:
        try:
            oldest_file = min(allFilePaths, key=os.path.getctime)
            os.remove(oldest_file)
            return oldest_file
        except Exception as e:
            LOGGER.exception("Failed to delete file {0}".format(oldest_file), exc_info=e)
            return None


# Directory
def create_missing_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def get_parent_dir(path):
    return os.path.dirname(path)


def get_dir_name(path):
    folder = path.split("/")[-1]
    return folder


if __name__ == "__main__":
    pass
