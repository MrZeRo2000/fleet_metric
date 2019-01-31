
from app import AppContext
from config import Configuration
from context import inject
import sys
from logging import Logger
from log import log_method
from app_config import AppConfig
from oracle_interface import OracleInterface, OracleLoader
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

    @property
    @inject
    def oracle_loader(self) -> OracleLoader:
        pass

    @log_method
    def configure(self):
        if len(self.__args) < 2:
            raise Exception("Configuration file name should be provided as first argument")

        self.configuration.load(self.__args[1])

        self.logger.setLevel(self.configuration.get().get("logging").get("level"))

        if self.configuration.get().get("logging").get("database_logging"):
            self.logger.addHandler(OracleLogHandler())

        return self

    @log_method
    def execute(self):
        try:
            if self.configuration.get().get("tasks").get("database_load"):
                self.oracle_loader.load()

            return self
        except Exception as e:
            self.logger.fatal(e, exc_info=True)
            exit(1)


Main(sys.argv).configure().execute()

