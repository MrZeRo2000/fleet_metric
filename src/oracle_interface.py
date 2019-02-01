
import os
import pandas as pd
import logging
from config import Configuration
from oracle_utils import OracleUtils
from context import inject, component
from app import AppContext
from log import log_method
from logging import Logger


@component
class OracleInterface:
    """
    Common Oracle interface class
    """

    @property
    @inject
    def configuration(self) -> Configuration: pass

    @property
    @inject
    def logger(self) -> Logger: pass

    def __init__(self):
        self.__ou = None

    @log_method
    def connect(self):
        connection_string = self.configuration.get().get("database").get("connection")
        self.__ou = OracleUtils(connection_string)

    def get(self) -> OracleUtils:
        if self.__ou is None:
            self.connect()
        return self.__ou


@component
class OracleLoader:
    """
    Oracle loader class
    """

    @property
    @inject
    def configuration(self) -> Configuration: pass

    @property
    @inject
    def logger(self) -> Logger: pass

    @property
    @inject
    def oracle_interface(self) -> OracleInterface: pass

    @log_method
    def load(self):
        """
        Loads data
        :return: None
        """

        file_name = self.configuration.get().get("data_files").get("data_file_name")
        full_file_name = os.path.abspath(os.path.join(os.path.dirname(__file__), file_name))
        load_stmt = self.configuration.get().get("database").get("load_stmt")
        load_stmt_str = "\n".join(load_stmt)

        self.logger.debug("Executing\n" + load_stmt_str)
        self.logger.debug("Destination path:" + full_file_name)

        self.oracle_interface.get().load_to_csv(load_stmt_str, full_file_name, self.configuration.CSV_DELIMITER)

    def load_train(self):
        """
        Loads train data
        :return: None
        """

        file_name = self.config.get_train_data_file_path()
        self.ou.load_to_csv("SELECT * FROM dn_ml_customer_train_view", file_name, Configuration.CSV_DELIMITER)

    def upload_result(self):
        """
        Uploads result data
        :return: None
        """

        file_name = self.config.get_result_data_file()

        stmt = "DELETE FROM dn_ml_customer_out"

        self.ou.execute_statement(stmt)
        self.ou.commit()

        stmt = "INSERT INTO dn_ml_customer_out (customer_no, trips_predict, trips,  trips_proba) VALUES (:1, :2, :3, :4)"

        df = pd.read_csv(file_name, sep=Configuration.CSV_DELIMITER)

        self.ou.bulk_insert(stmt, df)
        self.ou.commit()


class OracleLogHandler(logging.Handler):

    @inject
    def __init__(self, oi: OracleInterface):
        logging.Handler.__init__(self)
        self.__ou = oi.get()

    def emit(self, record):
        stmt = """
          INSERT INTO dn_ml_log (            
            module_name,
            logger_name,
            level_name,
            message,
            line_no,
            exc_name,
            exc_text
        ) VALUES (
            :module_name,
            :logger_name,
            :level_name,
            :message,
            :line_no,
            :exc_name,
            :exc_text        
        )
        """

        params = {
            "module_name": record.module,
            "logger_name": record.name,
            "level_name": record.levelname,
            "message": record.message,
            "line_no": record.lineno,
            "exc_name": None if record.exc_info is None else str(record.exc_info[1]),
            "exc_text": record.exc_text
        }

        self.__ou.execute_statement(stmt, params)
        self.__ou.commit()
