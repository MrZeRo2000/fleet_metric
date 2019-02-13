
from context import component, inject
import datetime
from config import Configuration
from logging import Logger
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from ps import PredictorService


@component
class ARIMAPredictionService(PredictorService):

    # noinspection PyPropertyDefinition
    @property
    @inject
    def configuration(self) -> Configuration: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def logger(self) -> Logger: pass

    def __init__(self):
        self.__df_m_p_ly = None
        self.__df_m_p_py = None
        self.__df_m_p = None
        self.__month_correction = 0
        self.__data_result = None

        self.__metric_forecast_field = None
        self.__metric_fact_field = None
        self.__metric_name_field = None

    def set_up(self):
        self.__metric_forecast_field = self.configuration.get().get("model").get("metric_forecast_field")
        self.__metric_fact_field = self.configuration.get().get("model").get("metric_fact_field")
        self.__metric_name_field = self.configuration.get().get("model").get("metric_name_field")

    def get_monthly_data(self):
        return self.__df_m_p_ly, self.__df_m_p_py

    def get_data_result(self):
        return self.__data_result, self.__df_m_p, self.__month_correction

    def calc_month_correction(self, df):
        # resampled to monthly
        df_m = df.resample('M', axis=0, label='right').mean()

        # percent changes
        df_m_p = df_m.pct_change().dropna()
        df_m_p.index = df_m_p.index.map(lambda x: datetime.datetime(x.year, x.month, 1))
        self.__df_m_p = df_m_p

        # last year
        self.__df_m_p_ly = df_m_p[df_m_p.index.max() - pd.DateOffset(years=1) + pd.DateOffset(months=1):df_m_p.index.max()]
        self.__df_m_p_py = df_m_p.shift(axis=0, periods=12)[df_m_p.index.max() - pd.DateOffset(years=1) + pd.DateOffset(months=1):df_m_p.index.max()]

        self.__month_correction = 0
        df_m_p_prev_month = df_m_p[df_m_p.index.max() - pd.DateOffset(months=11):df_m_p.index.max() - pd.DateOffset(months=11)]
        if not df_m_p_prev_month.empty > 0:
            self.__month_correction = df_m_p_prev_month[:1][self.__metric_name_field].values[0]

    def calc_test(self, df, predict_params):
        df_train = df[:-35]
        df_test = df[-35:]
        start_date = df_train.index.max() + pd.DateOffset(days=1)
        end_date = df_train.index.max() + pd.DateOffset(days=35)

        self.__data_result = self.predict(df_train, predict_params, start_date, end_date)
        self.__data_result[self.__metric_fact_field] = df_test[self.__metric_name_field].values

        # restrict with current month only
        self.__data_result = self.__data_result[df_test.index.max().replace(day=1):df_test.index.max()]

        last_day_prev = df_test.index.max() - datetime.timedelta(days=df_test.index.max().day)
        first_day_prev = last_day_prev.replace(day=1)

        result_forecast = self.__data_result[self.__metric_forecast_field].sum()
        result_fact = self.__data_result[self.__metric_fact_field].sum()
        result_prev = df[first_day_prev:last_day_prev][self.__metric_name_field].sum()

        return result_forecast, result_fact, result_prev

    def calc_predict(self, df, predict_params):
        start_date = df.index.max() + pd.DateOffset(days=1)
        end_date = start_date + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        self.__data_result = self.predict(df, predict_params, start_date, end_date)

        last_day_prev = df.index.max()
        first_day_prev = last_day_prev.replace(day=1)

        result_forecast = self.__data_result[self.__metric_forecast_field].sum()
        result_prev = df[first_day_prev:last_day_prev][self.__metric_name_field].sum()

        return result_forecast, result_prev

    def predict(self, df, predict_params, start_date, end_date):
        self.calc_month_correction(df)

        mod = SARIMAX(df, **predict_params)
        data_pred = mod.fit().predict(
            start=start_date,
            end=end_date
        ) * (1 + self.__month_correction)

        data_result = pd.DataFrame(data_pred)
        data_result.columns = [self.__metric_forecast_field]

        return data_result
