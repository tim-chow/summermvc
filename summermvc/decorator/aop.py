# coding: utf8

__all__ = ["aspect", "get_aspect", "is_aspect_present",
           "before", "get_before", "is_before_present",
           "around", "get_around", "is_around_present",
           "after_throwing", "get_after_throwing", "is_after_throwing_present",
           "after_returning", "get_after_returning", "is_after_returning_present",
           "after", "get_after", "is_after_present"]
__authors__ = ["Tim Chow"]

import inspect
import types  # used by AdviceFactory, DON'T DELETE IT

from ..reflect import get_declared_fields


def aspect(order):
    if not isinstance(order, int):
        raise ValueError("int expected")

    def _inner(cls):
        if not inspect.isclass(cls):
            raise RuntimeError("class expected")
        setattr(cls, "__aop_aspect__", order)
        return cls
    return _inner


def get_aspect(cls):
    if not inspect.isclass(cls):
        return None
    if "__aop_aspect__" not in get_declared_fields(cls, only_names=True):
        return None
    order = getattr(cls, "__aop_aspect__")
    if not isinstance(order, int):
        return None
    return order


def is_aspect_present(cls):
    return get_aspect(cls) is not None


class AdviceFactory(object):
    define_advice_type = "{{ADVICE_TYPE_PLACEHOLDER}}"

    advice = """\
def {{ADVICE_TYPE_PLACEHOLDER}}(point_cut):
    def _inner(f):
        if not isinstance(f, types.FunctionType):
            raise RuntimeError("function expected")
        setattr(
            f,
            "__aop_point_cut_{{ADVICE_TYPE_PLACEHOLDER}}__",
            point_cut)
        return f
    return _inner
"""

    get_advice = """\
def get_{{ADVICE_TYPE_PLACEHOLDER}}(f):
    if not isinstance(f, types.MethodType):
        raise RuntimeError("method expected")
    if "__aop_point_cut_{{ADVICE_TYPE_PLACEHOLDER}}__" not in get_declared_fields(f, only_names=True):
        return None
    attr_value = getattr(
        f, 
        "__aop_point_cut_{{ADVICE_TYPE_PLACEHOLDER}}__")
    if not isinstance(attr_value, basestring):
        return None
    return attr_value
"""

    is_advice_present = """\
def is_{{ADVICE_TYPE_PLACEHOLDER}}_present(f):
    return get_{{ADVICE_TYPE_PLACEHOLDER}}(f) is not None
"""

    @classmethod
    def create(cls, advice_type):
        if advice_type not in ["before", "around",
                               "after_throwing", "after_returning",
                               "after"]:
            raise ValueError("invalid advice type")
        _locals = {}
        exec(cls.advice.replace(cls.define_advice_type, advice_type),
             globals(),
             _locals)
        exec(cls.get_advice.replace(cls.define_advice_type, advice_type),
             globals(),
             _locals)
        exec(cls.is_advice_present.replace(cls.define_advice_type, advice_type),
             globals(),
             _locals)
        return (_locals[advice_type],
                _locals["get_" + advice_type],
                _locals["is_" + advice_type + "_present"])


before, get_before, is_before_present = AdviceFactory.create("before")
around, get_around, is_around_present = AdviceFactory.create("around")
after, get_after, is_after_present = AdviceFactory.create("after")
after_throwing, get_after_throwing, \
    is_after_throwing_present = AdviceFactory.create("after_throwing")
after_returning, get_after_returning, \
    is_after_returning_present = AdviceFactory.create("after_returning")
