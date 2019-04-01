
from context import inject
from context import component
from config import Configuration
from logging import Logger
from log import log_method
import pandas as pd
import datetime
import csv
import os


@component
class DataProcessorService:

    # noinspection PyPropertyDefinition
    @property
    @inject
    def configuration(self) -> Configuration: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def logger(self) -> Logger: pass

    @log_method
    def read_input_data(self):
        data_file_name = self.configuration.get().get("data_files").get("data_file_name")
        full_file_name = os.path.abspath(os.path.join(os.path.dirname(__file__), data_file_name))
        return pd.read_csv(full_file_name, self.configuration.CSV_DELIMITER)

    @log_method
    def split_input_data(self):
        df = self.read_input_data()
        ts_field = self.configuration.get().get("model").get("ts_field")
        category_field = self.configuration.get().get("model").get("category_field")
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")

        df.index = pd.to_datetime(df[ts_field], format="%d.%m.%Y")
        df = df.drop([ts_field], axis=1)

        dfr = {}
        categories = list(set(df[category_field]))
        for c in categories:
            d = df[df[category_field] == c]
            # d = df[df[category_field] == f].resample('M', axis=0, label='right').sum()
            # d.index = d.index.map(lambda x: datetime.datetime(x.year, x.month, 1))

            dfr[c] = d[[metric_name_field]]

        return dfr

    def get_file_name(self, file_param_name, category_id):
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")
        data_file_name = self.configuration.get().get("data_files").get(file_param_name)\
            .replace("{cat}", category_id).replace("{metric}", metric_name_field)
        full_file_name = os.path.abspath(os.path.join(os.path.dirname(__file__), data_file_name))
        return full_file_name

    def get_data_file_name(self, category_id):
        return self.get_file_name("data_file_cat_name", category_id)

    def get_result_file_name(self, category_id):
        return self.get_file_name("result_file_cat_name", category_id)

    def get_test_result_file_name(self, category_id):
        return self.get_file_name("test_result_file_cat_name", category_id)

    @log_method
    def save_input_data(self, df):
        for k in df.keys():
            data_file_name = self.get_data_file_name(k)
            df[k].to_csv(data_file_name,
                         self.configuration.CSV_DELIMITER,
                         mode='w',
                         header=True,
                         index=True,
                         quoting=csv.QUOTE_NONNUMERIC
                         )

    @log_method
    def save_split_data(self):
        self.save_input_data(self.split_input_data())

    def load_category_data(self, category_id):
        data_file_name = self.get_data_file_name(category_id)
        ts_field = self.configuration.get().get("model").get("ts_field")

        df = pd.read_csv(data_file_name, self.configuration.CSV_DELIMITER)

        df.index = pd.to_datetime(df[ts_field], format="%Y-%m-%d")
        df = df.drop([ts_field], axis=1).sort_index()

        return df

    def cleanup_data(self, df):
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")
        metric_threshold = int(self.configuration.get().get("model").get("metric_threshold"))

        return df[df[metric_name_field] > metric_threshold]

    def save_result_data(self, category_id, df):
        metric_fact_field = self.configuration.get().get("model").get("metric_fact_field")
        if metric_fact_field in df.columns:
            result_file_name = self.get_test_result_file_name(category_id)
        else:
            result_file_name = self.get_result_file_name(category_id)

        ts_field = self.configuration.get().get("model").get("ts_field")
        df.index.name = ts_field
        df.to_csv(result_file_name,
                  self.configuration.CSV_DELIMITER,
                  mode='w',
                  header=True,
                  index=True,
                  quoting=csv.QUOTE_NONNUMERIC
                  )

    def get_shifted_data(self, df, num_days=40, num_weeks=2):
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")

        # added daily shifted data

        for i in range(1, num_days + 1):
            df["fd" + str(i)] = df.copy().shift(i)[metric_name_field]

        # added weekly shifted data
        for i in range(1, num_weeks + 1):
            df["fw" + str(i)] = df.copy().shift(i * 7)[metric_name_field]

        # drop null values
        df = df.dropna()

        # add weekdays
        df_dow = pd.get_dummies(df.index.dayofweek, prefix="weekday", drop_first=True)
        df_dow.index = df.index

#        df_output = pd.concat([df_dow, df], axis=1)

        # add months
        df_mon = pd.get_dummies(df.index.month, prefix="month", drop_first=True)
        df_mon.index = df.index

        df_output = pd.concat([df_mon, pd.concat([df_dow, df], axis=1)], axis=1)

        # columns and labels
        features = [s for s in df_output.columns if s != metric_name_field]
        labels = [metric_name_field]

        return df_output, features, labels

    def get_pred_data(self, x_train, y_train, dt, num_days=40, num_weeks=2):
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")

        x_pred = x_train[-1:].copy()
        x_pred.index += pd.DateOffset(days=1)

        for i in range(2, 13):
            if i == dt.month:
                v = 1
            else:
                v = 0
            x_pred["month_" + str(i)] = v

        for i in range(1, 7):
            x_pred["weekday_" + str(i)] = x_train[-7:-6]["weekday_" + str(i)][0]

        for i in range(1, num_days + 1):
            x_pred["fd" + str(i)] = y_train[-i:][metric_name_field][0]

        for i in range(1, num_weeks + 1):
            x_pred["fw" + str(i)] = y_train[-i * 7:][metric_name_field][-1:][0]

        return x_pred

    @staticmethod
    def get_train_test_data(df):
        end_date = df.index.max()
        start_date = end_date.replace(day=1)

        df_train = df[:start_date - pd.DateOffset(days=1)]
        df_test = df[start_date:end_date]

        return df_train, df_test
