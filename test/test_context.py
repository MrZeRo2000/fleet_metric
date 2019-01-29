
from src.context import inject
from src.config import Configuration
from src.config import init_context
from src.config import get_context
from unittest import TestCase


class TestContext(TestCase):

    @staticmethod
    @inject
    def get_configuration():
        pass

    @staticmethod
    @inject
    def get_logger():
        pass

    def setUp(self):
        init_context()

    def test_configuration(self):
        configuration = TestContext.get_configuration()
        if configuration is None:
            print("No configuration is available")

        logger = TestContext.get_logger().get_logger()
        logger.info("Test log message")
