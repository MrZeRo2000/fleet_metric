
from src.context import inject
from app import AppContext
from app_config import AppConfig
from unittest import TestCase
from config import Configuration
from log import Logger


class ContextTestCase(TestCase):

    @property
    @inject
    def configuration(self) -> Configuration:
        pass

    @property
    @inject
    def logger(self) -> Logger:
        pass

    def setUp(self):
        AppConfig.execute()

