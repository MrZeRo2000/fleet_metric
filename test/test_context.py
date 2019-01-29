
from src.context import inject
from src.context import inject_p
from src.config import Configuration
from src.config import init_context
from src.config import get_context
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
        init_context()

    def test_configuration(self):
        configuration = self.configuration
        if configuration is None:
            print("No configuration is available")

        logger = self.logger
        logger.info("Test log message")
