
import os
import json
from context import component


@component
class Configuration:
    CONFIG_PATH = "cfg"
    """Log path"""

    CSV_DELIMITER = ';'
    """CSV file fields delimiter"""

    def __init__(self):
        self.__data = {}

    def load(self, file_name):
        config_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../" + self.CONFIG_PATH + "/" + file_name
            )
        )
        self.__data = dict(json.loads(open(config_path, mode='r').read()))

    def get(self) -> dict:
        return self.__data
