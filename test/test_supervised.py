
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


class TestSupervised(ContextTestCase):

    # noinspection PyPropertyDefinition
    @property
    @inject
    def data_processor_service(self) -> DataProcessorService: pass

    def setUp(self):
        ContextTestCase.setUp(self)
        context = AppContext.get_context()
        context.register_singleton_component(DataProcessorService())

        self.configuration.load("../test/cfg/test.json")
        self.category_id = "VIE"

        data_file_name = self.configuration.get().get("data_files").get("data_file_cat_name").replace("{metric}", "INCOME_NETTO").replace("{cat}", self.category_id)
        ts_field = self.configuration.get().get("model").get("ts_field")
        self.df = pd.read_csv(data_file_name, self.configuration.CSV_DELIMITER)
        self.df.index = pd.to_datetime(self.df[ts_field], format="%Y-%m-%d")
        self.df = self.df.drop([ts_field], axis=1).sort_index()

        self.show_plots = True

    def test1(self):
        df_train, df_test = self.data_processor_service.get_train_test_data(self.df)
        df_shifted, features, labels = self.data_processor_service.get_shifted_data(df_train, 35, 5, 12)

        XGBOOST_PARAM_ESTIMATORS = 10000
        XGBOOST_PARAM_DEPTH = 3
        XGBOOST_PARAM_LEARNING_RATE = 0.1

        predictor = xgboost.XGBRegressor(n_estimators=XGBOOST_PARAM_ESTIMATORS, max_depth=XGBOOST_PARAM_DEPTH,
                                         learning_rate=XGBOOST_PARAM_LEARNING_RATE)

        x_train = df_shifted[features]
        y_train = df_shifted[labels]

        y_test = df_test[labels]

        pass

    @skip
    def test_train_test(self):
        df_train, df_test = self.data_processor_service.get_train_test_data(self.df)

        self.assertEqual(len(self.df), len(df_train) + len(df_test))


