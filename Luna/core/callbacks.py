"""
Module containing callbacks related functions
"""

import os
from maya.api import OpenMaya as om2
from maya import cmds as mc
from Luna import Logger


def remove_licence_callback():
    """
    Adds  callback to remove student licence from saved file.

    :param data: user data to operate on, defaults to None
    :type data: any, optional
    :return: Info message
    :rtype: str
    """
    om2.MSceneMessage.addCallback(om2.MSceneMessage.kAfterSave, _remove_licence_line, None)
    return "Remove licence callback"


def _remove_licence_line(*args):
    """
    Removes student licence from current file if it is MAYA ASCII format.
    """
    path = mc.file(q=True, sn=True)
    if os.path.isfile(path) and path.endswith(".ma"):
        with open(path, 'r') as f:
            lines = f.readlines()
        with open(path, 'w') as f:
            for each in lines:
                if each.strip("\n") != 'fileInfo "license" "student";':
                    f.write(each)
            f.truncate()


if __name__ == "__main__":
    pass
