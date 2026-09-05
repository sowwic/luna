"""
Module containing callbacks related functions
"""

import os
from maya import cmds
from maya.api import OpenMaya


def remove_license_popup_callback() -> int:
    """
    Adds a callback to remove the student license line from the current file after saving.

    Returns:
        int: The callback ID for the added callback.
    """
    callback_id: int = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kAfterSave, _remove_license_line, None
    )
    return callback_id


def _remove_license_line(*args):
    """
    Removes student license from current file if it is MAYA ASCII format.

    Args:
        *args: Variable length argument list passed by the callback.
    """
    path: str = cmds.file(query=True, sceneName=True)
    if os.path.isfile(path) and path.endswith(".ma"):
        with open(path) as f:
            lines = f.readlines()
        with open(path, "w") as f:
            for each in lines:
                if each.strip("\n") != 'fileInfo "license" "student";':
                    f.write(each)
            f.truncate()
