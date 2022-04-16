# Modified from https://github.com/nxt-dev/nxt_editor/blob/release/nxt_editor/integration/maya/drag_into_maya.py

# Built-in
import os
import re

# External
from maya import cmds

ROOT_DIR = os.path.dirname(__file__)
CHANGELOG_FILE = os.path.join(ROOT_DIR, "CHANGELOG.rst")


def get_version_str_from_changelog():
    with open(CHANGELOG_FILE, "r") as versions_file:
        data = versions_file.read().rstrip()
    version = re.search(r'v\s*([\d.]+)', data).group(1) or "0.0.0"
    print("Latest version from changelog: {}".format(version))
    return version


def onMayaDroppedPythonFile(*args):
    """Dropped file maya callback entry point."""
    install_templates_dir = os.path.join(ROOT_DIR, "res", "templates", "install_files")
    template_mod_file = os.path.join(install_templates_dir, 'luna.mod')

    with open(template_mod_file, 'r') as fp:
        mod_content = fp.read()

    # Fill in template file
    mod_content = mod_content.replace('<LUNA_ROOT_PATH>', ROOT_DIR)
    mod_content = mod_content.replace("<LUNA_VERSION>", get_version_str_from_changelog())

    # Try to find modules directory
    user_maya_dir = os.environ.get('MAYA_APP_DIR')
    user_mods_dir = os.path.join(user_maya_dir, 'modules')
    if not os.path.isdir(user_mods_dir):
        os.makedirs(user_mods_dir)

    # Confirm modules directory
    caption = "Select maya modules directory"
    result = cmds.fileDialog2(caption=caption, dir=user_mods_dir, fileMode=2)
    chosen_dir = result[0]
    chosen_mod_path = os.path.join(chosen_dir, 'luna.mod')
    with open(chosen_mod_path, 'w+') as fp:
        fp.write(mod_content)
    print("Placed luna mod file at {}".format(chosen_mod_path))
    print("Please restart Maya and enable luna_plugin.py from plugin manager.")
