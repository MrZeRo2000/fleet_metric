
from context import component, inject
from config import Configuration
from logging import Logger
from ps import PredictorService
from dts import DataProcessorService
from log import log_method
from operator import methodcaller
import concurrent.futures


@component
class CalculationService:

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
    def data_processor_service(self) -> DataProcessorService: pass

    def __init__(self):
        self.__predictor_service = None

    @property
    def predictor_service(self) -> PredictorService:
        return self.__predictor_service

    @predictor_service.setter
    def predictor_service(self, value):
        self.__predictor_service = value

    def process_category(self, category_id):
        self.logger.info("Processing " + category_id)

        df = self.data_processor_service.load_category_data(category_id)
        df = self.data_processor_service.cleanup_data(df)
        predict_params = self.predictor_service.get_predict_params(category_id)
        self.logger.info("Params: " + str(predict_params))

        self.logger.info("Test calculation")
        self.predictor_service.set_up()
        self.predictor_service.calc_test(df, predict_params)
        data_result = self.predictor_service.get_data_result()

        df_result = data_result[0]
        self.data_processor_service.save_result_data(category_id, df_result)

        self.logger.info("Test calculation completed")

        self.logger.info("Predict calculation")
        self.predictor_service.calc_predict(df, predict_params)
        data_result = self.predictor_service.get_data_result()

        df_result = data_result[0]
        self.data_processor_service.save_result_data(category_id, df_result)

        self.logger.info("Predict calculation completed")

        self.logger.info("Processed " + category_id)

    @log_method
    def process_tasks(self):
        categories = self.configuration.get().get("tasks").get("categories")
        list(map(self.process_category, categories))

    @log_method
    def process_tasks_parallel(self):
        categories = self.configuration.get().get("tasks").get("categories")
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            executor.map(self.process_category, categories)
