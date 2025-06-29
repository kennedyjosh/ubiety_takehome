from util import *


def test_singleton():
    class SingletonChild(metaclass=Singleton):
        pass

    assert SingletonChild() is SingletonChild()

    class NotSingleton():
        pass

    assert NotSingleton() is not NotSingleton()


def test_env():
    assert is_test_env()
