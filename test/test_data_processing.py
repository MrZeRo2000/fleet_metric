
from unittest import TestCase
from test_common import ContextTestCase
import pandas as pd
import datetime


class TestDataProcessing(ContextTestCase):

    def setUp(self):
        ContextTestCase.setUp(self)
        self.configuration.load("../test/cfg/test.json")

        data_file_name = self.configuration.get().get("data_files").get("data_file_name")
        print("Data file name:" + data_file_name)
        self.df = pd.read_csv(data_file_name, self.configuration.CSV_DELIMITER)

    def testDataFile(self):
        df = self.df

        print("Length:" + str(len(df)))

        fleets = list(set(df["CATEGORY_ID"]))
        print("Fleets:" +str(fleets))

        df_f_len = 0
        for f in fleets:
            df_f = df[df["CATEGORY_ID"] == f]
            df_f_len += len(df_f)
            print("For fleet=", f, " length=", len(df_f))

        print("Total length=", df_f_len)
        self.assertEqual(len(df), df_f_len)

    def testPrepareData(self):
        df = self.df[self.df["CATEGORY_ID"] == "VIE"]

        df.index = pd.to_datetime(df["DAY_ID"], format="%d.%m.%Y")
        df = df.drop(["DAY_ID"], axis=1)

        # resample to month
        df_r = df.resample('M', axis=0, label='right').sum()

        # map to month start (just for beauty)
        df_r.index = df_r.index.map(lambda x: datetime.datetime(x.year, x.month, 1))

        pass

    def testPrepareDictData(self):
        df = self.df

        df.index = pd.to_datetime(df["DAY_ID"], format="%d.%m.%Y")
        df = df.drop(["DAY_ID"], axis=1)

        dfr = {}
        fleets = list(set(df["CATEGORY_ID"]))
        for f in fleets:
            d = df[df["CATEGORY_ID"] == f].resample('M', axis=0, label='right').sum()
            d.index = d.index.map(lambda x: datetime.datetime(x.year, x.month, 1))

            dfr[f] = d

        pass


