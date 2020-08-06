import pymel.core as pm
from Luna.core.loggingFn import Logger
from Luna.static import Directories


Logger.set_level(10)


def open_port(port=7221, lang="python"):
    if not pm.commandPort("127.0.0.1:{0}".format(port), n=1, q=1):
        try:
            pm.commandPort(name="127.0.0.1:{0}".format(port), stp=lang, echoOutput=True)
            Logger.info("Command port opened: Python - 7221")
        except Exception as e:
            Logger.exception("Failed to open command port", exc_info=e)


def run():
    Logger.write_to_rotating_file(Directories.LOG_FILE, level=30)
    Logger.info("Logging to file: {0}".format(Directories.LOG_FILE))
    open_port()
