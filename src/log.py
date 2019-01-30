
from functools import wraps
import datetime
import logging
import os


class Formatter(logging.Formatter):
    def format(self, record):
        record.module = record.args["module"]
        return super(Formatter, self).format(record)


class Logger:
    LOG_FILE_FORMAT = "log_{0:04d}-{1:02d}-{2:02d}.txt"
    """Log file format"""

    LOG_PATH = "log"
    """Log path"""

    LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(module)s %(message)s"
    """Log format"""

    def __init__(self, name):
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(logging.DEBUG)

        today = datetime.datetime.now()

        log_path = os.path.join(os.path.dirname(__file__), "../" + self.LOG_PATH)

        log_file_name = os.path.join(log_path, self.LOG_FILE_FORMAT.format(today.year, today.month, today.day))
        formatter = Formatter(self.LOG_FORMAT)

        file_handler = logging.FileHandler(log_file_name)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(console_handler)

    @property
    def logger(self) -> logging.Logger:
        return self.__logger


def log_method(func):
    def wrapper(*args, **kwargs):
        logger = func.__globals__.get("AppContext").get_context().components.get(Logger.__name__)
        func_name = args[0].__class__.__name__ + "." + func.__name__
        module_name = args[0].__class__.__module__.strip("__")
        logger.info(func_name + " started", {"module": module_name})
        result = func(*args, **kwargs)
        logger.info(func_name + " completed", {"module": module_name})
        return result

    return wrapper

