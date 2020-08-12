import sys
import inspect
import logging
import logging.handlers
from PySide2 import QtCore
import pymel.core as pm


class Logger:

    LOGGER_NAME = "Luna"
    LEVEL_DEFAULT = logging.DEBUG
    PROPAGATE_DEFAULT = False
    FORMAT_DEFAULT = "[{0}][%(levelname)s] %(message)s"
    _logger_obj = None  # type: logging.Logger
    _signal_handler = None  # type: QSignalHandler

    @classmethod
    def logger_obj(cls):
        """Returns logger object

        :return: Logger object
        :rtype: logging.Logger
        """
        if not cls._logger_obj:
            if cls.logger_exists():
                cls._logger_obj = logging.getLogger(cls.LOGGER_NAME)
            else:
                cls._logger_obj = logging.getLogger(cls.LOGGER_NAME)
                cls._logger_obj.setLevel(cls.LEVEL_DEFAULT)
                cls.set_propagate(cls.PROPAGATE_DEFAULT)
                # Formatters
                fmt = logging.Formatter(cls.FORMAT_DEFAULT.format(cls.LOGGER_NAME), datefmt="%d-%m-%Y %H:%M:%S")
                qt_fmt = logging.Formatter("[%(levelname)s] %(message)s")
                # Handlers
                stream_handler = logging.StreamHandler(sys.stdout)
                stream_handler.setFormatter(fmt)
                cls._signal_handler = QSignalHandler()
                cls._signal_handler.setFormatter(qt_fmt)
                cls._logger_obj.addHandler(stream_handler)
                cls._logger_obj.addHandler(cls._signal_handler)

        return cls._logger_obj

    @classmethod
    def logger_exists(cls):
        return cls.LOGGER_NAME in logging.Logger.manager.loggerDict.keys()

    @classmethod
    def set_level(cls, level):
        lg = cls.logger_obj()
        lg.setLevel(level)

    @classmethod
    def get_level(cls, name=False):
        if name:
            return logging.getLevelName(cls.logger_obj().level)
        return cls.logger_obj().level

    @classmethod
    def set_propagate(cls, propagate):
        lg = cls.logger_obj()
        lg.propagate = propagate

    @classmethod
    def signal_handler(cls):
        cls.logger_obj()
        return cls._signal_handler

    @classmethod
    def call_info(cls, message):
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        message = "file: {0} function {1}() lineno:{2}-{3}".format(caller.filename, caller.function, caller.lineno, message)

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.info(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.warning(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.error(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.critical(msg, *args, **kwargs)

    @classmethod
    def log(cls, level, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.log(level, msg, *args, **kwargs)

    @classmethod
    def exception(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.exception(msg, *args, **kwargs)

    @classmethod
    def write_to_rotating_file(cls, path, level=logging.WARNING, mode="w", max_bytes=1024):
        lg = cls.logger_obj()
        if any([isinstance(handler, logging.handlers.RotatingFileHandler) for handler in lg.handlers]):
            lg.warning("Rotating file hander already exists")
            return

        rfile_hander = logging.handlers.RotatingFileHandler(path, mode=mode, maxBytes=max_bytes, backupCount=0, delay=0)
        rfile_hander.setLevel(level)
        fmt = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
        rfile_hander.setFormatter(fmt)

        lg.addHandler(rfile_hander)


class MGlobalHandler(logging.Handler):
    def __init__(self, level="DEBUG"):
        super(MGlobalHandler, self).__init__(level)

    def emit(self, record):
        msg = self.format(record)
        if record.levelname in ["DEBUG", "INFO"]:
            pm.displayInfo(msg)
        elif record.levelname == "WARNING":
            pm.displayWarning(msg)
        elif record.levelname in ["ERROR", "CRITICAL"]:
            pm.displayError(msg)


class QSignaler(QtCore.QObject):
    message_logged = QtCore.Signal(str)


class QSignalHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super(QSignalHandler, self).__init__(*args, **kwargs)
        self.emitter = QSignaler()

    def emit(self, record):
        msg = self.format(record)
        self.emitter.message_logged.emit(msg)


if __name__ == "__main__":
    testLogger = Logger.logger_obj().handlers
