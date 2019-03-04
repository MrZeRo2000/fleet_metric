
from unittest import TestCase
from unittest import skip
from test_common import ContextTestCase
import re
import glob
import pandas as pd
import os
import matplotlib.pyplot as plt


class TestDisplayResult(ContextTestCase):
    def setUp(self):
        ContextTestCase.setUp(self)
        self.configuration.load("../test/cfg/test.json")
        self.test_result_file_cat_name = self.configuration.get().get("data_files").get("test_result_file_cat_name")

    def testDisplayResult(self):
        ts_field = self.configuration.get().get("model").get("ts_field")

        file_mask = re.sub('({.+?})', '*', self.test_result_file_cat_name)
        file_list = glob.glob(file_mask)

        self.assertGreater(len(file_list), 0)

        for f in file_list:
            print(f)
            df = pd.read_csv(f, sep=self.configuration.CSV_DELIMITER, index_col=ts_field, parse_dates=True)
            self.assertFalse(df.empty)

            result_name = os.path.basename(f)
            result_name = re.split('_', result_name)[-1:][0]
            result_name = re.split('\.', result_name)[0]

            self.display_result(df, result_name)

    def display_result(self, df, result_name):
        metric_forecast_field = self.configuration.get().get("model").get("metric_forecast_field")
        metric_fact_field = self.configuration.get().get("model").get("metric_fact_field")
        result_pic_file_name = self.configuration.get().get("data_files").get("result_pic_file_name")

        err = (df[metric_forecast_field].sum() - df[metric_fact_field].sum()) / df[metric_fact_field].sum()

        plt.clf()
        plt.plot(df)
        plt.title(result_name + " Error: {0:.2f}%".format(err * 100))
        plt.savefig(result_pic_file_name.replace('{cat}', result_name))


