
from src.context import inject
from app import AppContext
from unittest import TestCase
from config import Configuration
import log
import logging


class ContextTestCase(TestCase):

    # noinspection PyPropertyDefinition
    @property
    @inject
    def configuration(self) -> Configuration: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def logger(self) -> logging.Logger: pass

    def setUp(self):
        context = AppContext.get_context()
        context.register_singleton_component(Configuration())
        context.register_singleton_component(log.Logger().logger)

