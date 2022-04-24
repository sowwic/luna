import pymel.core as pm
import os
import luna
from luna import Logger
from PySide2 import QtWidgets


def clear_all_references(*args):
    references = pm.listReferences()
    for r in references:
        r.remove()


def browse_model():
    current_asset = luna.workspace.Asset.get()
    file_filters = "Maya (*.ma *mb);;Maya ASCII (*.ma);;Maya Binary(*.mb);;All Files (*.*)"
    selected_filter = "Maya (*.ma *mb)"
    model_path = QtWidgets.QFileDialog.getOpenFileName(
        None, "Select model file", current_asset.path, file_filters, selected_filter)[0]
    if not model_path:
        return ""

    return model_path


def import_model(browse_if_not_found=False):
    current_asset = luna.workspace.Asset.get()
    model_path = current_asset.model_path
    if not os.path.isfile(model_path) and not browse_if_not_found:
        Logger.warning("Model import | Invalid model file path: {}".format(model_path))
        return

    # Try browsing
    if not os.path.isfile(model_path):
        model_path = browse_model()
        current_asset.set_data("model", model_path)

    # If still not a valid file - return
    if not os.path.isfile(model_path):
        Logger.warning("Model import | Invalid model file path: {}".format(model_path))
        return

    try:
        pm.importFile(model_path)
    except RuntimeError as e:
        Logger.exception("Failed to load model file: {0}".format(model_path))
        raise e
    Logger.info("Imported model: {0}".format(model_path))
    return model_path


def reference_model(*args):
    current_asset = luna.workspace.Asset.get()
    if current_asset:
        pm.createReference(current_asset.model_path)
    else:
        pm.warning("Asset is not set!")


def import_skeleton():
    current_asset = luna.workspace.Asset.get()
    latest_skeleton_path = current_asset.latest_skeleton_path
    pm.importFile(latest_skeleton_path, loadReferenceDepth="none", dns=1)
    Logger.info("Imported skeleton: {0}".format(latest_skeleton_path))
    return latest_skeleton_path


def increment_save_file(typ="skeleton"):
    current_asset = luna.workspace.Asset.get()
    if not current_asset:
        pm.warning("Asset is not set!")
    new_file = getattr(current_asset, "new_{0}_path".format(typ))
    pm.saveAs(new_file)
    Logger.info("Saved {0}: {1}".format(typ, new_file))


def save_file_as(typ="skeleton"):
    current_asset = luna.workspace.Asset.get()
    if not current_asset:
        pm.warning("Asset is not set!")
    start_dir = getattr(current_asset, typ)
    file_path, filters = QtWidgets.QFileDialog.getSaveFileName(
        None, "Save {0} as".format(typ), start_dir)
    if file_path:
        pm.saveAs(file_path)
        Logger.info("Saved {0}: {1}".format(typ, file_path))
