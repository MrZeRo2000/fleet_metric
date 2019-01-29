
class ComponentFactory:
    _instance = None
    components = {}

    def register_singleton_component(self, component):
        component_id = component.__class__.__name__
        if component_id not in self.components:
            self.components[component_id] = component

    def get_component(self, component):
        return self.components[component.__class__.__name__]

    @staticmethod
    def _get_instance():
        if ComponentFactory._instance is None:
            ComponentFactory._instance = ComponentFactory()

        return ComponentFactory._instance

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
    def wrapper():
        component_id = func.__name__.split("_")[1].capitalize()
        get_context_func = func.__globals__.get('get_context')
        return get_context_func().components[component_id]

    return wrapper


def get_context():
    return ComponentFactory._get_instance()
