
from context import component, inject
import datetime
from config import Configuration
from logging import Logger
import pandas as pd
from ps import PredictorService
from dts import DataProcessorService
import xgboost
from log import log_method


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

        self.__month_correction = 0
        self.__df_m_p = None

    def set_up(self):
        self.__metric_forecast_field = self.configuration.get().get("model").get("metric_forecast_field")
        self.__metric_fact_field = self.configuration.get().get("model").get("metric_fact_field")
        self.__metric_name_field = self.configuration.get().get("model").get("metric_name_field")

    def get_predict_params(self, category_id=None):
        return self.configuration.get().get("model").get("supervised_parameters")

    @log_method
    def get_shifted_data(self, df, num_days=40, num_weeks=2):
        df = df.copy()

        # added daily shifted data
        for i in range(1, num_days + 1):
            df["fd" + str(i)] = df.copy().shift(i)[self.__metric_name_field]

        # added weekly shifted data
        for i in range(1, num_weeks + 1):
            df["fw" + str(i)] = df.copy().shift(i * 7)[self.__metric_name_field]

        # drop null values
        df = df.dropna()

        # add weekdays
        df_dow = pd.get_dummies(df.index.dayofweek, prefix="weekday", drop_first=True)
        df_dow.index = df.index

        # add months
        # df_mon = pd.get_dummies(df.index.month, prefix="month", drop_first=True)
        # df_mon.index = df.index

        df_output = pd.concat([df_dow, df], axis=1)

        # columns and labels
        features = [s for s in df_output.columns if s != self.__metric_name_field]
        labels = [self.__metric_name_field]

        return df_output, features, labels

    def get_pred_data(self, x_train, y_train, dt, num_days=40, num_weeks=2):

        x_pred = x_train[-1:].copy()
        x_pred.index += pd.DateOffset(days=1)

        # for i in range(2, 13):
        #     if i == dt.month:
        #         v = 1
        #     else:
        #         v = 0
        #     x_pred["month_" + str(i)] = v

        for i in range(1, 7):
            x_pred["weekday_" + str(i)] = x_train[-7:-6]["weekday_" + str(i)][0]

        for i in range(1, num_days + 1):
            x_pred["fd" + str(i)] = y_train[-i:][self.__metric_name_field][0]

        for i in range(1, num_weeks + 1):
            x_pred["fw" + str(i)] = y_train[-i * 7:][self.__metric_name_field][-1:][0]

        return x_pred

    @log_method
    def calc_test(self, df, predict_params):
        df_train, df_test = self.data_processor_service.get_train_test_data(df)

        self.__data_result = self.predict(df_train, predict_params)

        start_date = self.__data_result.index.min()
        end_date = self.__data_result.index.max()

        self.__data_result[self.__metric_fact_field] = df_test[start_date:end_date][self.__metric_name_field]

        last_day_prev = df_test.index.max() - pd.DateOffset(days=df_test.index.max().day)
        first_day_prev = last_day_prev.replace(day=1)

        result_forecast = self.__data_result[self.__metric_forecast_field].sum()
        result_fact = self.__data_result[self.__metric_fact_field].sum()
        result_prev = df[first_day_prev:last_day_prev][self.__metric_name_field].sum()

        return result_forecast, result_fact, result_prev

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

    @log_method
    def calc_predict(self, df, predict_params):
        self.__data_result = self.predict(df, predict_params)

        last_day_prev = df.index.max()
        first_day_prev = last_day_prev.replace(day=1)

        result_forecast = self.__data_result[self.__metric_forecast_field].sum()
        result_prev = df[first_day_prev:last_day_prev][self.__metric_name_field].sum()

        return result_forecast, result_prev

    @log_method
    def predict(self, df, predict_params):
        self.calc_month_correction(df)

        num_days = predict_params["num_days"]
        num_weeks = predict_params["num_weeks"]

        df_shifted, features, labels = self.get_shifted_data(
            df,
            num_days,
            num_weeks
        )

        predictor = xgboost.XGBRegressor(**predict_params)

        x_train = df_shifted[features]
        y_train = df_shifted[labels]

        start_date = x_train.index.max() + pd.DateOffset(days=1)

        # for dn in range(0, 3):
        for dn in range(0, start_date.days_in_month):
            d = start_date + pd.DateOffset(days=dn)

            self.logger.debug("Calculating {}".format(d))

            x_pred = self.get_pred_data(x_train, y_train, d, num_days, num_weeks)

            predictor.fit(x_train, y_train.values.ravel())

            y_pred = predictor.predict(x_pred)

            x_train = x_train.append(x_pred)

            y_train_new = y_train[-1:].copy()
            y_train_new.iloc[0][0] = y_pred.ravel()
            y_train_new.index += pd.DateOffset(days=1)

            y_train = y_train.append(y_train_new)

        end_date = y_train.index.max()

        y_train.columns = [self.__metric_forecast_field]

        return y_train[start_date:end_date] * (1 + self.__month_correction)

    def get_data_result(self):
        return self.__data_result, self.__df_m_p, self.__month_correction
