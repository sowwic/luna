"""
Module containing callbacks related functions
"""
import os
import pymel.core as pm
import pymel.api as pma


def remove_licence_popup_callback():
    """
    Adds  callback to remove student licence from saved file.

    :param data: user data to operate on, defaults to None
    :type data: any, optional
    :return: Info message
    :rtype: str
    """
    pma.MSceneMessage.addCallback(pma.MSceneMessage.kAfterSave, _remove_licence_line, None)
    return "Remove licence callback"


def _remove_licence_line(*args):
    """
    Removes student licence from current file if it is MAYA ASCII format.
    """
    path = pm.sceneName()
    if os.path.isfile(path) and path.endswith(".ma"):
        with open(path, 'r') as f:
            lines = f.readlines()
        with open(path, 'w') as f:
            for each in lines:
                if each.strip("\n") != 'fileInfo "license" "student";':
                    f.write(each)
            f.truncate()
