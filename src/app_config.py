
from app import AppContext
from config import Configuration
from log import Logger
from oracle_interface import OracleInterface, OracleLoader


class AppConfig:
    @staticmethod
    def execute():
        context = AppContext.get_context()
        context.register_singleton_component(Configuration())
        context.register_singleton_component(Logger().logger)
        context.register_singleton_component(OracleInterface())
        context.register_singleton_component(OracleLoader())
