
from unittest import TestCase
from unittest import skip
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
        self.category_id = "VIE"

        data_file_name = self.configuration.get().get("data_files").get("data_file_cat_name").replace("{cat}", self.category_id)
        ts_field = self.configuration.get().get("model").get("ts_field")
        self.df = pd.read_csv(data_file_name, self.configuration.CSV_DELIMITER)
        self.df.index = pd.to_datetime(self.df[ts_field], format="%Y-%m-%d")
        self.df = self.df.drop([ts_field], axis=1).sort_index()

        self.show_plots = True

    def test1(self):
        df = self.df
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")
        metric_threshold = int(self.configuration.get().get("model").get("metric_threshold"))
        # to include working data
        df = df[df[metric_name_field] > metric_threshold]

        # resampled to monthly
        df_m = df.resample('M', axis=0, label='right').mean()

        # percent changes
        df_m_p = df_m.pct_change().dropna()
        df_m_p.index = df_m_p.index.map(lambda x: datetime.datetime(x.year, x.month, 1))

        df_m_p_ly = df_m_p[df_m_p.index.max() - pd.DateOffset(years=1) + pd.DateOffset(months=1):df_m_p.index.max()]
        df_m_p_py = df_m_p.shift(axis=0, periods=12)[df_m_p.index.max() - pd.DateOffset(years=1) + pd.DateOffset(months=1):df_m_p.index.max()]

        month_correction = 0
        if len(df_m_p_py) > 0:
            month_correction = df_m_p_py[-1:][metric_name_field].values[0]

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

        df_train = df[:-35]
        df_test = df[-35:]

        # BER:mod = SARIMAX(df_train, order=(2, 1, 1), seasonal_order=(3, 0, 1, 7))
        # VIE:mod = SARIMAX(df_train, order=(14, 0, 1), seasonal_order=(2, 1, 1, 7))
        # BRU:mod = SARIMAX(df_train, order=(20, 1, 2), seasonal_order=(3, 0, 1, 7))
        # CGN:mod = SARIMAX(df_train, order=(20, 1, 1), seasonal_order=(3, 1, 1, 7)) - potential common configuration
        # CPH:mod = SARIMAX(df_train, order=(20, 1, 1), seasonal_order=(3, 1, 1, 7))
        # DUS:mod = SARIMAX(df_train, order=(14, 0, 1), seasonal_order=(2, 1, 1, 7))
        # HAM:mod = SARIMAX(df_train, order=(20, 1, 1), seasonal_order=(3, 1, 1, 7)) !! BAD RESULT: trend in data
        # HEL:mod = SARIMAX(df_train, order=(20, 1, 1), seasonal_order=(3, 1, 1, 7))
        # LIS:mod = SARIMAX(df_train, order=(20, 1, 1), seasonal_order=(3, 1, 1, 7)) !! BAD RESULT
        # LON:mod = SARIMAX(df_train, order=(20, 1, 3))
        # MIL:mod = SARIMAX(df_train, order=(20, 1, 1), seasonal_order=(3, 1, 1, 7)) !! BAD RESULT: trend in data
        # MUC:mod = SARIMAX(df_train, order=(16, 1, 4))

        mod = SARIMAX(df_train, **self.configuration.get().get("model").get("sarimax_parameters")[self.category_id])
        data_pred = mod.fit().predict(
            start=df_train.index.max() + pd.DateOffset(days=1),
            end=df_train.index.max() + pd.DateOffset(days=35)
        ) * (1 + month_correction)

        data_result = pd.DataFrame(data_pred)
        data_result.columns = ["forecast"]
        data_result["fact"] = df_test[metric_name_field].values
#        data_result.index = df_test.index

        # restrict with current month only
        data_result = data_result[df_test.index.max().replace(day=1):df_test.index.max()]

        last_day_prev = df_test.index.max() - datetime.timedelta(days=df_test.index.max().day)
        first_day_prev = last_day_prev.replace(day=1)

        result_forecast = data_result["forecast"].sum()
        result_fact = data_result["fact"].sum()
        result_prev = df[first_day_prev:last_day_prev][metric_name_field].sum()

        print("Fact: {0:.2f}".format(result_fact))
        print("Forecast: {0:.2f}".format(result_forecast))
        print("Previous: {0:.2f}".format(result_prev))
        print("Month correction: {0:.2f}%".format(month_correction*100))
        print("Prediction error: {0:.2f}%".format(abs(result_fact - result_forecast) / result_fact * 100))

        if self.show_plots:
            data_result.plot()
            plt.show()

    @skip
    def testMonthly(self):
        self.show_plots = True

        df = self.df

        # resampled to monthly
        df_m = df.resample('M', axis=0, label='right').mean()

        # percent changes
        df_m_p = df_m.pct_change().dropna()
        df_m_p.index = df_m_p.index.map(lambda x: datetime.datetime(x.year, x.month, 1))

        df_train = df_m_p[:-1]
        df_test = df_m_p[-1:]

        df_train_ly = df_train[df_train.index.max() - pd.DateOffset(years=1) + pd.DateOffset(months=1):df_train.index.max()]
        df_train_py = df_train.shift(axis=0, periods=12)[df_train.index.max() - pd.DateOffset(years=1) + pd.DateOffset(months=1):df_train.index.max()]

        pass

        if self.show_plots:
            plt.plot(df_train)
            plt.show()

            plt.subplot(2, 1, 1)
            plt.title("Last year")
            plt.plot(df_train_ly)

            plt.subplot(2, 1, 2)
            plt.title("Previous year")
            plt.plot(df_train_py)

            plt.show()

        pass