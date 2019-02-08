
from unittest import TestCase
from test_common import ContextTestCase
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller


class TestDataAnalysis(ContextTestCase):
    def setUp(self):
        ContextTestCase.setUp(self)
        self.configuration.load("../test/cfg/test.json")

        data_file_name = self.configuration.get().get("data_files").get("data_file_cat_name").replace("{cat}", "VIE")
        ts_field = self.configuration.get().get("model").get("ts_field")
        self.df = pd.read_csv(data_file_name, self.configuration.CSV_DELIMITER)
        self.df.index = pd.to_datetime(self.df[ts_field], format="%Y-%m-%d")
        self.df = self.df.drop([ts_field], axis=1).sort_index()

        self.show_plots = False

    def test1(self):
        df = self.df
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")
        df_y_s = df.resample('M', axis=0, label='right').sum()
        df_y_m = df.resample('M', axis=0, label='right').mean()

        if self.show_plots:
            plt.plot(df)
            plt.show()

            plt.plot(df_y_s)
            plt.title("Monthly sum")
            plt.show()

            plt.plot(df_y_m)
            plt.title("Monthly mean")
            plt.show()

            plot_acf(df, lags=50, alpha=0.05)
            plot_pacf(df, lags=50, alpha=0.05)
            plt.show()

        df_train = df[:-35]
        df_test = df[-35:]

        # mod = SARIMAX(df_train, order=(8, 1, 2), seasonal_order=(3, 0, 1, 7))
        mod = SARIMAX(df_train, order=(14, 1, 2))
        res = mod.fit()
        data_pred = res.predict(start=df_test.index.min(), end=df_test.index.max()).values

        data_result = pd.DataFrame(data_pred)
        data_result.columns = ["forecast"]
        data_result["fact"] = df_test[metric_name_field].values
        data_result.index = df_test.index

        # restrict with current month only
        data_result = data_result[df_test.index.max().replace(day=1):df_test.index.max()]

        last_day_prev = df_test.index.max() - datetime.timedelta(days=df_test.index.max().day)
        first_day_prev = last_day_prev.replace(day=1)

        result_forecast = data_result["forecast"].sum()
        result_fact = data_result["fact"].sum()
        result_prev = df[first_day_prev:last_day_prev][metric_name_field].sum()

        print("Fact:", result_fact)
        print("Forecast:", result_forecast)
        print("Previous:", result_prev)

        if self.show_plots:
            data_result.plot()
            plt.show()


