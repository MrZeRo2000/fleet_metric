
import logging
import datetime
import os
from context import get_context

class Configuration:
    def __init__(self):
        print("Configuration init")


class Logger:
    LOG_FILE_FORMAT = "log_{0:04d}-{1:02d}-{2:02d}.txt"
    """Log file format"""

    LOG_PATH = "log"
    """Log path"""

    LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
    """Log format"""

    def __init__(self, name):
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(logging.DEBUG)

        today = datetime.datetime.now()

        log_path = os.path.join(os.path.dirname(__file__), "../" + self.LOG_PATH)

        log_file_name = os.path.join(log_path, self.LOG_FILE_FORMAT.format(today.year, today.month, today.day))
        formatter = logging.Formatter(self.LOG_FORMAT)

        file_handler = logging.FileHandler(log_file_name)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(console_handler)

    @property
    def logger(self):
        return self.__logger


def init_context():
    context = get_context()
    context.register_singleton_component(Configuration())
    context.register_singleton_component(Logger("ts_metrics").logger)
