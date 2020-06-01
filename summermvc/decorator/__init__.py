# coding: utf8

from .component import *
from .aop import *
from .mvc import *


# 仅仅是一个标记，表明重写了父类中的方法或
# + 实现了接口中的方法
def override(f):
    return f


def builtin(obj):
    setattr(obj, "__built_into_builtin__", True)
    return obj


def is_builtin_present(obj):
    from ..reflect import get_declared_attribute
    try:
        return get_declared_attribute(obj, "__built_into_builtin__") is True
    except ValueError:
        return False
