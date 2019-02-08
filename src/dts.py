
from context import inject
from context import component
from config import Configuration
from logging import Logger
from log import log_method
import pandas as pd
import datetime
import csv


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
        return pd.read_csv(data_file_name, self.configuration.CSV_DELIMITER)

    @log_method
    def split_input_data(self):
        df = self.read_input_data()
        ts_field = self.configuration.get().get("model").get("ts_field")
        category_field = self.configuration.get().get("model").get("category_field")
        metric_name_field = self.configuration.get().get("model").get("metric_name_field")

        df.index = pd.to_datetime(df[ts_field], format="%d.%m.%Y")
        df = df.drop([ts_field], axis=1)

        dfr = {}
        fleets = list(set(df[category_field]))
        for f in fleets:
            d = df[df[category_field] == f]
            # d = df[df[category_field] == f].resample('M', axis=0, label='right').sum()
            # d.index = d.index.map(lambda x: datetime.datetime(x.year, x.month, 1))

            dfr[f] = d[[metric_name_field]]

        return dfr

    @log_method
    def save_input_data(self, df):
        for k in df.keys():
            data_file_name = self.configuration.get().get("data_files").get("data_file_cat_name").replace("{cat}", k)
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
