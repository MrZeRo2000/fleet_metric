
from src.context import inject
from app import AppContext
from unittest import TestCase
from test_common import ContextTestCase


class TestConfiguration(ContextTestCase):
    def test_database(self):
        self.configuration.load("../test/cfg/test.json")
        config = self.configuration.get()
        config_db = config.get("database")
        self.assertEqual("drivenow_bi/drivenow_bi@sxbistax", config_db.get("connection"))
        self.assertFalse(config_db.get("logging"))
        self.assertEqual("SELECT x FROM dual", " ".join(config_db.get("load_stmt")))
        calc_stmt = config_db.get("calc_stmt")
        self.assertEqual("", calc_stmt)
