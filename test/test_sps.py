import unittest
from test_common import ContextTestCase
from context import inject
from app import AppContext
from dts import DataProcessorService
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
import pandas as pd
from sps import SupervisedPredictionService


class TestSPS(ContextTestCase):

    # noinspection PyPropertyDefinition
    @property
    @inject
    def data_processor_service(self) -> DataProcessorService: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def supervised_prediction_service(self) -> SupervisedPredictionService: pass

    def setUp(self):
        ContextTestCase.setUp(self)
        context = AppContext.get_context()
        context.register_singleton_component(DataProcessorService())
        context.register_singleton_component(SupervisedPredictionService())

        self.configuration.load("../test/cfg/test.json")
        self.category_id = "VIE"

        self.show_plots = True

    def testSPS(self):
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")
        df = self.data_processor_service.load_category_data("VIE")
        df = self.data_processor_service.cleanup_data(df)
        predict_params = self.configuration.get().get("model").get("supervised_parameters")

        sps = self.supervised_prediction_service
        sps.set_up()
        result_forecast, result_fact, result_prev = sps.calc_test(df, predict_params)
        data_result = sps.get_data_result()

        print("Forecast: {0:.2f}".format(result_forecast))
        print("Fact: {0:.2f}".format(result_fact))
        print("Previous: {0:.2f}".format(result_prev))
        print("Prediction error: {0:.2f}%".format(abs(result_fact - result_forecast) / result_fact * 100))

        if self.show_plots:
            plt.plot(df)
            plt.show()

            data_result.plot()
            plt.title("Test results")
            plt.show()
