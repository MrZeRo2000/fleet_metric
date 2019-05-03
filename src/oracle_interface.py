
import os
import pandas as pd
import logging
from config import Configuration
from oracle_utils import OracleUtils
from context import inject
from context import component
from log import log_method
from logging import Logger
from dts import DataProcessorService


@component
class OracleInterface:
    """
    Common Oracle interface class
    """

    # noinspection PyPropertyDefinition
    @property
    @inject
    def configuration(self) -> Configuration: pass

    # noinspection PyPropertyDefinition
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
    def oracle_interface(self) -> OracleInterface: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def data_processor_service(self) -> DataProcessorService: pass

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

    @log_method
    def upload_result(self):
        """
        Uploads result data
        :return: None
        """

        metric_name_field = self.configuration.get().get("model").get("metric_name_field")
        metric_name_table_field  = self.configuration.get().get("model").get("metric_name_table_field")
        category_field = self.configuration.get().get("model").get("category_field")
        categories = self.configuration.get().get("tasks").get("categories")
        ou = self.oracle_interface.get()

        metric_params = {"metric_name": metric_name_field}

        stmt = "DELETE FROM dn_ml_metric_test_out WHERE metric_name = :metric_name"
        ou.execute_statement(stmt, metric_params)
        ou.commit()

        stmt = "DELETE FROM dn_ml_metric_out WHERE metric_name = :metric_name"
        ou.execute_statement(stmt, metric_params)
        ou.commit()

        stmt = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'"
        ou.execute_statement(stmt)

        for c in categories:
            self.logger.debug("Processing result " + c)
            result_file_name = self.data_processor_service.get_result_file_name(c)

            if os.path.isfile(result_file_name):
                df_r = pd.read_csv(result_file_name, sep=self.configuration.CSV_DELIMITER)
                df_r[category_field] = c
                df_r[metric_name_table_field] = metric_name_field

                stmt = "INSERT INTO dn_ml_metric_out (day_id, forecast, category_id, metric_name) VALUES (:1, :2, :3, :4)"
                ou.bulk_insert(stmt, df_r)
                ou.commit()
                self.logger.debug("Processed result " + c)
            else:
                self.logger.debug("Result not found for " + c)

            self.logger.debug("Processing test result " + c)
            test_result_file_name = self.data_processor_service.get_test_result_file_name(c)

            if os.path.isfile(test_result_file_name):
                df_t = pd.read_csv(test_result_file_name, sep=self.configuration.CSV_DELIMITER)
                df_t[category_field] = c
                df_t[metric_name_table_field] = metric_name_field

                stmt = "INSERT INTO dn_ml_metric_test_out (day_id, forecast, fact, category_id, metric_name) VALUES (:1, :2, :3, :4, :5)"
                ou.bulk_insert(stmt, df_t)
                ou.commit()
                self.logger.debug("Processed test result " + c)
            else:
                self.logger.debug("Test result not found for " + c)


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
