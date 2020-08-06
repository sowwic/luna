import sys
import inspect
import logging
import logging.handlers


class Logger:

    LOGGER_NAME = "Luna"
    LEVEL_DEFAULT = logging.DEBUG
    _logger_obj = None  # type: logging.Logger

    @classmethod
    def logger_obj(cls):
        """Returns logger objec

        :return: Logger object
        :rtype: logging.Logger
        """
        if not cls._logger_obj:
            if cls.logger_exists():
                cls._logger_obj = logging.getLogger(cls.LOGGER_NAME)
            else:
                cls._logger_obj = logging.getLogger(cls.LOGGER_NAME)
                cls._logger_obj.setLevel(cls.LEVEL_DEFAULT)
                fmt = logging.Formatter("[{0}][%(levelname)s] %(message)s".format(cls.LOGGER_NAME), datefmt="%d-%m-%Y %H:%M:%S")
                stream_handler = logging.StreamHandler(sys.stderr)
                stream_handler.setFormatter(fmt)
                cls._logger_obj.addHandler(stream_handler)

        cls._logger_obj.propagate = 0

        return cls._logger_obj

    @classmethod
    def logger_exists(cls):
        return cls.LOGGER_NAME in logging.Logger.manager.loggerDict.keys()

    @classmethod
    def set_level(cls, level):
        lg = cls.logger_obj()
        lg.setLevel(level)

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
    def write_to_rotating_file(cls, path, level=logging.WARNING):
        lg = cls.logger_obj()
        if any([isinstance(handler, logging.handlers.RotatingFileHandler) for handler in lg.handlers]):
            lg.warning("Rotating file hander already exists")
            return

        rfile_hander = logging.handlers.RotatingFileHandler(path, mode="a", maxBytes=1024, backupCount=0, delay=0)
        rfile_hander.setLevel(level)
        fmt = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
        rfile_hander.setFormatter(fmt)

        lg.addHandler(rfile_hander)
