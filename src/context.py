
class ComponentFactory:
    __instance = None
    components = {}

    def register_singleton_component(self, component):
        component_id = component.__class__.__name__
        if component_id not in self.components:
            self.components[component_id] = component

    def get_component(self, component):
        return self.components[component.__class__.__name__]

    def match_component_by_type(self, component_type: type):
        result = list(filter(lambda c: type(c) == component_type, self.components.values()))
        if len(result) > 0:
            return result[0]

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
        if func.__annotations__ is None:
            return func(args, kwargs)

        ctx = func.__globals__.get('AppContext').get_context().get_instance()

        for (arg_key, arg_type) in func.__annotations__.items():
            instance_required = arg_key not in kwargs
            if instance_required and arg_key != 'return':
                kwargs[arg_key] = ctx.match_component_by_type(arg_type)
                return func(*args, **kwargs)

        return_type = func.__annotations__['return']
        return ctx.match_component_by_type(return_type)

    return wrapper
