from config import Configuration
from log import Logger
from context import ComponentFactory


class AppContext:
    @staticmethod
    def get_context():
        return ComponentFactory.get_instance()

    @staticmethod
    def init_context():
        context = AppContext.get_context()
        context.register_singleton_component(Configuration())
        context.register_singleton_component(Logger("ts_metrics").logger)