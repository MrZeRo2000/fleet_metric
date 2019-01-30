from app import AppContext
from config import Configuration
from context import inject
import sys
from logging import Logger
from log import log_method


class Main:
    def __init__(self, args):
        self.__args = args
        AppContext.init_context()

    @property
    @inject
    def configuration(self) -> Configuration:
        pass

    @property
    @inject
    def logger(self) -> Logger:
        pass

    @log_method
    def configure(self):
        if len(self.__args) < 2:
            raise Exception("Configuration file name should be provided as first argument")

    @log_method
    def execute(self):
        try:
            self.configure()
        except Exception as e:
            self.logger.fatal(e, exc_info=True)
            exit(1)


Main(sys.argv).execute()
