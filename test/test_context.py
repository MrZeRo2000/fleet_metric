
from test_common import ContextTestCase


class TestContext(ContextTestCase):

    def test_configuration(self):
        configuration = self.configuration
        if configuration is None:
            print("No configuration is available")

        logger = self.logger
        logger.info("Test log message")
