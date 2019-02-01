
from app import AppContext
from config import Configuration
from log import Logger
from oracle_interface import OracleInterface, OracleLoader
import pkgutil
import importlib
import inspect
import sys


class AppConfig:
    @staticmethod
    def execute():
        context = AppContext.get_context()

        context.register_singleton_component(Configuration())
        context.register_singleton_component(Logger().logger)
        context.register_singleton_component(OracleInterface())
        context.register_singleton_component(OracleLoader())

"""        
        cc = set()
        for pkg in [p[1] for p in pkgutil.iter_modules(__file__) if p[1] != __name__]:
            importlib.import_module(pkg)
            component_funcs = [x[1] for x in inspect.getmembers(sys.modules[pkg])
                               if inspect.isfunction(x[1])
                               and 'return' in x[1].__annotations__
                               and x[1].__qualname__.split(".")[0] == 'component']
            
            for cf in component_funcs:
                cls = cf.__annotations__['return']
                cc.add(cls)
        
        for c in cc:
            c_instance = c()
            context.register_singleton_component(c_instance)
"""
"""        
        context.register_singleton_component(Configuration())
        context.register_singleton_component(Logger().logger)
        context.register_singleton_component(OracleInterface())
        context.register_singleton_component(OracleLoader())
"""
"""
cc = set()
for pkg in [p[1] for p in pkgutil.iter_modules(__file__) if p[1] != __name__]:
    importlib.import_module(pkg)
    component_funcs = [x[1] for x in inspect.getmembers(sys.modules[pkg])
                       if inspect.isfunction(x[1])
                       and 'return' in x[1].__annotations__
                       and x[1].__qualname__.split(".")[0] == 'component']

    for cf in component_funcs:
        cls = cf.__annotations__['return']
        cc.add(cls)

for c in cc:
    c_instance = c()
    context.register_singleton_component(c_instance)
"""