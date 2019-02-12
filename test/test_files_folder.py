

from unittest import TestCase
import glob
import os


class TestFilesFolder(TestCase):
    def test1(self):

        files = [f for f in os.listdir("../data/") if f.find("ts_metrics_out") != -1 or f.find("ts_metrics_test_out") != -1]
        print(files)