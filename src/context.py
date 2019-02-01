
import inspect


class ComponentFactory:
    __instance = None
    components = {}

    def register_singleton_component(self, cls_component):
        component_id = cls_component.__class__.__name__
        if component_id not in self.components:
            self.components[component_id] = cls_component

    def get_component(self, cls_component):
        return self.components[cls_component.__class__.__name__]

    def match_component_by_type(self, component_type):
        # result = list(filter(lambda c: type(c) == component_type, self.components.values()))
        while inspect.isfunction(component_type):
            component_type = component_type.__annotations__['return']
        result = [c for c in self.components.values() if type(c) == component_type]
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

        from app import AppContext
        ctx = AppContext.get_context()

        for (arg_key, arg_type) in func.__annotations__.items():
            instance_required = arg_key not in kwargs
            if instance_required and arg_key != 'return':
                while inspect.isfunction(arg_type):
                    arg_type = arg_type.__annotations__['return']
                kwargs[arg_key] = ctx.match_component_by_type(arg_type)
                return func(*args, **kwargs)

        return_type = func.__annotations__['return']
        while inspect.isfunction(return_type):
            return_type = return_type.__annotations__['return']

        return ctx.match_component_by_type(return_type)

    return wrapper


def component(cls):
    def on_call(*args, **kwargs) -> cls:
        print("component loaded:" + str(cls))
        return cls(*args, **kwargs)
    return on_call
