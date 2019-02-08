
from app import AppContext
from config import Configuration
from context import inject
import sys
from logging import Logger
from log import log_method
from oracle_interface import OracleLoader
from oracle_interface import OracleLogHandler
from dts import DataProcessorService


class Main:
    def __init__(self, args):
        self.__args = args
        # AppConfig.execute()
        AppContext.initialize_context(__file__)

    # noinspection PyPropertyDefinition
    @property
    @inject
    def configuration(self) -> Configuration: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def logger(self) -> Logger: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def oracle_loader(self) -> OracleLoader: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def data_processor_service(self) -> DataProcessorService: pass

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

            df = self.data_processor_service.process_input_data()
            self.data_processor_service.save_input_data(df)

            df_pred = df["VIE"]

            return self
        except Exception as e:
            self.logger.fatal(e, exc_info=True)
            exit(1)


if __name__ == "__main__":
    Main(sys.argv).configure().execute()

