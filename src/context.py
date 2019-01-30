

class ComponentFactory:
    __instance = None
    components = {}

    def register_singleton_component(self, component):
        component_id = component.__class__.__name__
        if component_id not in self.components:
            self.components[component_id] = component

    def get_component(self, component):
        return self.components[component.__class__.__name__]

    @staticmethod
    def get_instance():
        if ComponentFactory.__instance is None:
            ComponentFactory.__instance = ComponentFactory()

        return ComponentFactory.__instance

"""
def inject(context=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            component_id = func.__name__.split("_")[1].capitalize()
            return context.components[component_id]

        return wrapper
    return decorator
"""


def inject(func):
    def wrapper(*args, **kwargs):
        data = func.__name__.split("_")
        if len(data) == 1:
            component_id = data[0].capitalize()
        else:
            component_id = data[1].capitalize()
        return func.__globals__.get('AppContext').get_context().get_instance().components[component_id]

    return wrapper


"""
def get_context():
    return ComponentFactory._get_instance()
"""