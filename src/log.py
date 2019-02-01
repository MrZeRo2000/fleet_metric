
import datetime
import logging
import os
from context import component


class Formatter(logging.Formatter):
    def format(self, record):

        if len(record.args) == 0:
            module = record.module
        else:
            module = str(record.args["module"])

        if hasattr(record, "message"):
            message = record.message
        else:
            if hasattr(record, "msg"):
                message = str(record.msg)
            else:
                message = "No message for " + str(record)

        record.module = module
        record.message = message

        return super(Formatter, self).format(record)


@component
class Logger:
    LOG_FILE_FORMAT = "log_{0:04d}-{1:02d}-{2:02d}.txt"
    """Log file format"""

    LOG_PATH = "log"
    """Log path"""

    LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(module)s %(message)s"
    """Log format"""

    COMPONENT_PROPERTY_NAME = "logger"

    def __init__(self):
        name = __file__.split(os.path.sep)[-3]

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
        from app import AppContext
        ctx = AppContext.get_context()
        logger = ctx.match_component_by_type(logging.Logger)

        func_name = args[0].__class__.__name__ + "." + func.__name__
        module_name = args[0].__class__.__module__.strip("__")
        module_info = {"module": module_name}

        logger.info(func_name + " started", module_info)
        result = func(*args, **kwargs)
        logger.info(func_name + " completed", module_info)

        return result

    return wrapper

