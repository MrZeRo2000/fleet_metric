
import pandas as pd
import logging
from config import Configuration
from oracle_utils import OracleUtils
from context import inject
from app import AppContext
from log import log_method
from log import Logger


class OracleInterface:
    """
    Common Oracle interface class
    """

    @property
    @inject
    def configuration(self) -> Configuration:
        pass

    @property
    @inject
    def logger(self) -> Logger:
        pass

    def __init__(self):
        self.__ou = None

    @log_method
    def connect(self):
        connection_string = self.configuration.get().get("database").get("connection")
        self.__ou = OracleUtils(connection_string)

    def get(self):
        if self.__ou is None:
            self.connect()
        return self.__ou


class OracleLoader(OracleInterface):
    """
    Oracle loader class
    """

    def __init__(self, config_file_name):
        super().__init__(config_file_name)

    def load_pred(self):
        """
        Loads prediction data
        :return: None
        """

        file_name = self.config.get_predict_data_file_path()
        self.ou.load_to_csv("SELECT * FROM dn_ml_customer_pred_view", file_name, Configuration.CSV_DELIMITER)

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

    def __init__(self, config_file_name):
        logging.Handler.__init__(self)

        oi = OracleInterface(config_file_name)
        self.ou = oi.ou

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

        self.ou.execute_statement(stmt, params)
        self.ou.commit()
