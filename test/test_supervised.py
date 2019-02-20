
from unittest import TestCase
from unittest import skip
from test_common import ContextTestCase
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from dts import DataProcessorService
from app import AppContext
from context import inject
import xgboost
import numpy as np
from sps import SupervisedPredictionService


class TestSupervised(ContextTestCase):

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

        data_file_name = self.configuration.get().get("data_files").get("data_file_cat_name").replace("{metric}", "INCOME_NETTO").replace("{cat}", self.category_id)
        ts_field = self.configuration.get().get("model").get("ts_field")
        self.df = pd.read_csv(data_file_name, self.configuration.CSV_DELIMITER)
        self.df.index = pd.to_datetime(self.df[ts_field], format="%Y-%m-%d")
        self.df = self.df.drop([ts_field], axis=1).sort_index()

        self.show_plots = True

    @skip
    def test1(self):
        df_train, df_test = self.data_processor_service.get_train_test_data(self.df)
        df_shifted, features, labels = self.data_processor_service.get_shifted_data(df_train, 5, 2)

        XGBOOST_PARAM_ESTIMATORS = 10000
        XGBOOST_PARAM_DEPTH = 3
        XGBOOST_PARAM_LEARNING_RATE = 0.1

        predictor = xgboost.XGBRegressor(n_estimators=XGBOOST_PARAM_ESTIMATORS, max_depth=XGBOOST_PARAM_DEPTH,
                                         learning_rate=XGBOOST_PARAM_LEARNING_RATE)

        x_train = df_shifted[features]
        y_train = df_shifted[labels]

        y_test = df_test[labels]

        start_date = x_train.index.max() + pd.DateOffset(days=1)
        y_pred = np.empty((0,))

        #for dn in range(0, start_date.days_in_month):
        for dn in range(0, 3):
            d = start_date + pd.DateOffset(days=dn)

            x_pred = self.data_processor_service.get_pred_data(x_train, y_train, d, 5, 2)

            predictor.fit(x_train, y_train.values.ravel())

            y_pred = predictor.predict(x_pred)

            x_train = x_train.append(x_pred)

            y_train_new = y_train[-1:].copy()
            y_train_new.iloc[0][0] = y_pred.ravel()
            y_train_new.index += pd.DateOffset(days=1)

            y_train = y_train.append(y_train_new)


    @skip
    def test_pred_df(self):
        dt = pd.to_datetime('01.02.2019', format='%d.%m.%Y')
        df = pd.DataFrame(index=[dt])

    @skip
    def test_train_test(self):
        df_train, df_test = self.data_processor_service.get_train_test_data(self.df)

        self.assertEqual(len(self.df), len(df_train) + len(df_test))

    @skip
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

    def testMonthly(self):
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")
        df = self.data_processor_service.load_category_data("VIE")
        df = self.data_processor_service.cleanup_data(df)
        df_m = df.resample('M', axis=0, label='right').mean()

        df_m_p = df_m.pct_change().dropna()
        df_m_p.index = df_m_p.index.map(lambda x: datetime.datetime(x.year, x.month, 1))

        for i in range(1, 13):
            df_m_p["fm" + str(i)] = df_m_p.copy().shift(i)[metric_name_field]

        df_m_p = df_m_p.dropna()

        df_train = df_m_p[:-1]
        df_test = df_m_p[-1:]

        features = [s for s in df_m_p.columns if s != metric_name_field]
        labels = [metric_name_field]

        x_train = df_train[features]
        y_train = df_train[labels]

        x_test = df_test[features]
        y_test = df_test[labels]

        x_pred = df_train[-1:].copy().shift(1, axis=1)[features]

        XGBOOST_PARAM_ESTIMATORS = 10000
        XGBOOST_PARAM_DEPTH = 3
        XGBOOST_PARAM_LEARNING_RATE = 0.1

        predictor = xgboost.XGBRegressor(n_estimators=XGBOOST_PARAM_ESTIMATORS, max_depth=XGBOOST_PARAM_DEPTH,
                                         learning_rate=XGBOOST_PARAM_LEARNING_RATE)

        predictor.fit(x_train, y_train.values.ravel())

        y_pred = predictor.predict(x_pred)

        pass