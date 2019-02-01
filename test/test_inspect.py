
from functools import wraps
from unittest import TestCase
import inspect
import importlib
import sys


def component(cls):
    def on_call(*args, **kwargs) -> cls:
        print("component on call")
        return cls(*args, **kwargs)
    return on_call


@component
class TestComponent:
    def __init__(self):
        print("creating  TestComponent")


@component
class TestComponent2:
    def __init__(self):
        print("creating  TestComponent2")


class TestInspect(TestCase):

    def setUp(self):
        importlib.import_module("test_common")
        self.classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)

    def test_classes(self):
        print(self.classes)

    def test_component(self):
        classes = inspect.getmembers(sys.modules[__name__])
        component_funcs = [x[1] for x in inspect.getmembers(sys.modules[__name__])
                      if inspect.isfunction(x[1])
                      and 'return' in x[1].__annotations__
                      and x[1].__qualname__.split(".")[0] == 'component']
        print(component_funcs)
        for cf in component_funcs:
            cls = cf.__annotations__['return']
            cls()
