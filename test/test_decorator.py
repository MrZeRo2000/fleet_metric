
from functools import wraps
from unittest import TestCase


def log_decorator(func):
    @wraps(func)
    def log_wrapper(*args, **kwargs):
        print("Before function " + func.__name__)
        func(*args, **kwargs)
        print("After function")
    return log_wrapper


singleton_instances = {}


def singleton(a_class):
    def on_call(*args, **kwargs):
        print("In onCall")
        if a_class not in singleton_instances:
            print("Creating new instance")
            singleton_instances[a_class] = a_class(*args, **kwargs)
        else:
            print("Using existing instance")
        return singleton_instances[a_class]
    return on_call


def sample_func(x):
    print("Func: x=" + str(x))


@singleton
class Configuration:
    def __init__(self):
        print("Create instance of Configuration")

@log_decorator
def decorated_func(x):
    print("Decorated func: x=" + str(x))


class TestDecoratedFunc(TestCase):

    def test_func(self):
        sample_func(14)

    def test_decorated_func(self):
        decorated_func(14)
        decorated_func(x=20)


class TestDecoratedClass(TestCase):

    def test1(self):
        print("Before configuration instance creation")
        config = Configuration()
        print("After configuration instance creation")
        print("Before configuration instance creation 2")
        config = Configuration()
        print("After configuration instance creation 2")
