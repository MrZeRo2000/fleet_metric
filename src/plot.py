
from app import AppContext
from config import Configuration
from context import inject
import sys
from logging import Logger
from log import log_method
import re
import glob
import pandas as pd
import os
import matplotlib.pyplot as plt


class PlotTest:

    def __init__(self, args):
        self.__args = args
        # AppConfig.execute()
        AppContext.initialize_context(__file__)

    # noinspection PyPropertyDefinition
    @property
    @inject
    def configuration(self) -> Configuration: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def logger(self) -> Logger: pass

    def display_result(self, df, result_name):
        metric_forecast_field = self.configuration.get().get("model").get("metric_forecast_field")
        metric_fact_field = self.configuration.get().get("model").get("metric_fact_field")
        result_pic_file_name = self.configuration.get().get("data_files").get("result_pic_file_name")

        err = (df[metric_forecast_field].sum() - df[metric_fact_field].sum()) / df[metric_fact_field].sum()

        plt.clf()
        plt.plot(df)
        plt.title(result_name + " Error: {0:.2f}%".format(err * 100))
        plt.savefig(result_pic_file_name.replace('{cat}', result_name))

    @log_method
    def configure(self):
        if len(self.__args) < 2:
            raise Exception("Configuration file name should be provided as first argument")

        self.configuration.load(self.__args[1])

        self.logger.setLevel(self.configuration.get().get("logging").get("level"))

        return self

    @log_method
    def execute(self):
        test_result_file_cat_name = self.configuration.get().get("data_files").get("test_result_file_cat_name")
        ts_field = self.configuration.get().get("model").get("ts_field")

        file_mask = re.sub('({.+?})', '*', test_result_file_cat_name)
        file_list = glob.glob(file_mask)

        self.logger.debug("Read results: {} files".format(len(file_list)))

        for f in file_list:
            self.logger.debug("Processing {}".format(f))

            df = pd.read_csv(f, sep=self.configuration.CSV_DELIMITER, index_col=ts_field, parse_dates=True)

            result_name = os.path.basename(f)
            result_name = re.split('_', result_name)[-1:][0]
            result_name = re.split('\.', result_name)[0]

            self.display_result(df, result_name)


if __name__ == "__main__":
    PlotTest(sys.argv).configure().execute()

