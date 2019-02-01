
import pkgutil
import importlib
import inspect
import sys
import os

from context import ComponentFactory


class AppContext:
    @staticmethod
    def get_context():
        return ComponentFactory.get_instance()

    @staticmethod
    def initialize_context(module_name):
        context = AppContext.get_context()

        components = set()
        for pkg_name in [p[1] for p in pkgutil.iter_modules([os.path.dirname(module_name)]) if p[1] != __name__]:
            importlib.import_module(pkg_name)
            component_funcs = [x[1] for x in inspect.getmembers(sys.modules[pkg_name])
                               if inspect.isfunction(x[1])
                               and 'return' in x[1].__annotations__
                               and x[1].__qualname__.split(".")[0] == 'component']

            for cf in component_funcs:
                components.add(cf)

        for c in components:
            c_instance = c()
            if hasattr(c_instance, "COMPONENT_PROPERTY_NAME"):
                component_property_name = getattr(c_instance, "COMPONENT_PROPERTY_NAME")
                context.register_singleton_component(getattr(c_instance, component_property_name))
            else:
                context.register_singleton_component(c_instance)

