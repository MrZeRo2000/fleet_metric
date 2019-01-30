
from src.context import inject
from app import AppContext
from unittest import TestCase


class TestContext(TestCase):

    @property
    @inject
    def configuration(self):
        pass

    @property
    @inject
    def logger(self):
        pass

    def setUp(self):
        AppContext.init_context()

    def test_configuration(self):
        configuration = self.configuration
        if configuration is None:
            print("No configuration is available")

        logger = self.logger
        logger.info("Test log message")
