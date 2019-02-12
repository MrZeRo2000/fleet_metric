
import unittest
from test_common import ContextTestCase
from aps import ARIMAPredictionService
from context import inject
from app import AppContext
from dts import DataProcessorService
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
import pandas as pd


class TestDataAnalysis(ContextTestCase):

    # noinspection PyPropertyDefinition
    @property
    @inject
    def data_processor_service(self) -> DataProcessorService: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def arima_prediction_service(self) -> ARIMAPredictionService: pass

    def setUp(self):
        ContextTestCase.setUp(self)
        context = AppContext.get_context()
        context.register_singleton_component(DataProcessorService())
        context.register_singleton_component(ARIMAPredictionService())

        self.configuration.load("../test/cfg/test.json")
        self.category_id = "VIE"

        self.show_plots = True

#    @unittest.skip
    def testAPS(self):
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")
        df = self.data_processor_service.load_category_data("VIE")
        df = self.data_processor_service.cleanup_data(df)
        predict_params = self.configuration.get().get("model").get("sarimax_parameters")["VIE"]

        aps = self.arima_prediction_service
        aps.set_up()
        result_forecast, result_fact, result_prev = aps.calc_test(df, predict_params)
        data_result, df_m_p, month_correction = aps.get_data_result()

        df_m_p_ly = df_m_p[df_m_p.index.max() - pd.DateOffset(years=1) + pd.DateOffset(months=1):df_m_p.index.max()]
        df_m_p_py = df_m_p.shift(axis=0, periods=12)[df_m_p.index.max() - pd.DateOffset(years=1) + pd.DateOffset(months=1):df_m_p.index.max()]


        print("Forecast: {0:.2f}".format(result_forecast))
        print("Fact: {0:.2f}".format(result_fact))
        print("Previous: {0:.2f}".format(result_prev))
        print("Month correction: {0:.2f}%".format(month_correction*100))
        print("Prediction error: {0:.2f}%".format(abs(result_fact - result_forecast) / result_fact * 100))

        if self.show_plots:
            plt.plot(df)
            plt.show()

            plot_acf(df, lags=50, alpha=0.05)
            plt.show()
            plot_pacf(df, lags=50, alpha=0.05)
            plt.show()

            ly, = plt.plot(df_m_p_ly.index, df_m_p_ly[metric_name_field].values * 100)
            py, = plt.plot(df_m_p_ly.index, df_m_p_py[metric_name_field].values * 100)
            plt.legend((ly, py), ("Last year", "Previous year"))
            plt.title("Monthly metric percent changes")
            plt.grid()
            plt.show()

            data_result.plot()
            plt.title("Test results")
            plt.show()

#    @unittest.skip
    def testAPSPredict(self):
        df = self.data_processor_service.load_category_data("VIE")
        df = self.data_processor_service.cleanup_data(df)
        predict_params = self.configuration.get().get("model").get("sarimax_parameters")["VIE"]

        aps = self.arima_prediction_service
        aps.set_up()
        result_forecast, result_prev = aps.calc_predict(df, predict_params)

        data_result, df_m_p, month_correction = aps.get_data_result()

        print("Forecast: {0:.2f}".format(result_forecast))
        print("Previous: {0:.2f}".format(result_prev))
        print("Month correction: {0:.2f}%".format(month_correction*100))

        if self.show_plots:
            data_result.plot()
            plt.title("Prediction")
            plt.show()
