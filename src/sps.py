
from context import component, inject
import datetime
from config import Configuration
from logging import Logger
import pandas as pd
from ps import PredictorService
from dts import DataProcessorService
import xgboost


@component
class SupervisedPredictionService(PredictorService):

    # noinspection PyPropertyDefinition
    @property
    @inject
    def configuration(self) -> Configuration: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def data_processor_service(self) -> DataProcessorService: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def logger(self) -> Logger: pass

    def __init__(self):
        self.__data_result = None

        self.__metric_forecast_field = None
        self.__metric_fact_field = None
        self.__metric_name_field = None

    def set_up(self):
        self.__metric_forecast_field = self.configuration.get().get("model").get("metric_forecast_field")
        self.__metric_fact_field = self.configuration.get().get("model").get("metric_fact_field")
        self.__metric_name_field = self.configuration.get().get("model").get("metric_name_field")

    def calc_test(self, df, predict_params):
        pass

    def calc_predict(self, df, predict_params):
        raise NotImplementedError("Method predict_test not implemented")

    def get_data_result(self):
        raise NotImplementedError("Method predict_test not implemented")
