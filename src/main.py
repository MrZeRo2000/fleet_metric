
from app import AppContext
from config import Configuration
from context import inject
import sys
from logging import Logger
from log import log_method
from app_config import AppConfig
from oracle_interface import OracleInterface
from oracle_interface import OracleLogHandler


class Main:
    def __init__(self, args):
        self.__args = args
        AppConfig.execute()

    @property
    @inject
    def configuration(self) -> Configuration:
        pass

    @property
    @inject
    def logger(self) -> Logger:
        pass

    @property
    @inject
    def oracle_interface(self) -> OracleInterface:
        pass

    @log_method
    def configure(self):
        if len(self.__args) < 2:
            raise Exception("Configuration file name should be provided as first argument")
        self.configuration.load(self.__args[1])
        # ou = self.oracle_interface.get()
        if self.configuration.get().get("database").get("logging"):
            self.logger.addHandler(OracleLogHandler())

    @log_method
    def execute(self):
        try:
            self.configure()
        except Exception as e:
            self.logger.fatal(e, exc_info=True)
            exit(1)


Main(sys.argv).execute()
