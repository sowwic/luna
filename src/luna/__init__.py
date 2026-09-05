import re
import os

from maya import cmds

from luna.static.vars import *
from luna.core.logger import Logger
from luna.core.config import Config
import luna.workspace


def get_version_from_changelog():
    root_path: str = cmds.moduleInfo(moduleName="luna", path=True)  # type: str
    changelog_file = os.path.join(root_path, "CHANGELOG.rst")
    with open(changelog_file) as versions_file:
        data = versions_file.read().rstrip()
    version = re.search(r"v\s*([\d.]+)", data).group(1) or "0.0.0"
    print(f"Latest version from changelog: {version}")
    return version


__version__ = get_version_from_changelog()
