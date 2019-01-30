from context import ComponentFactory


class AppContext:
    @staticmethod
    def get_context():
        return ComponentFactory.get_instance()

