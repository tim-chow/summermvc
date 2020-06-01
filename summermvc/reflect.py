# coding: utf8

__all__ = ["get_declared_methods",
           "get_declared_field",
           "get_declared_fields",
           "get_declared_attribute",
           "get_declared_attributes"]
__authors__ = ["Tim Chow"]

import inspect
import types


def get_declared_methods(cls, only_names=False):
    """返回类中定义的所有实例方法"""
    if not inspect.isclass(cls):
        raise ValueError("class expected")
    for attr_name in vars(cls):
        attr = getattr(cls, attr_name)
        if not isinstance(attr, types.UnboundMethodType):
            continue
        if only_names:
            yield attr_name
        else:
            yield attr_name, attr


def __is_function(attr_value):
    return isinstance(attr_value, staticmethod) or \
           isinstance(attr_value, classmethod) or \
           isinstance(attr_value, types.FunctionType) or \
           isinstance(attr_value, types.MethodType)


def get_declared_field(obj, field_type, only_names=False):
    """返回对象或类中定义的特定类型的所有属性（不包含方法）"""
    if not inspect.isclass(field_type):
        raise StopIteration("class expected")

    for attr_name, attr_value in vars(obj).iteritems():
        if __is_function(attr_value):
            continue
        if not isinstance(attr_value, field_type):
            continue
        if only_names:
            yield attr_name
        else:
            yield attr_name, attr_value


def get_declared_fields(obj, only_names=False):
    """返回对象或类中定义的所有属性（不包含方法）"""
    for attr_name, attr_value in vars(obj).iteritems():
        if __is_function(attr_value):
            continue
        if only_names:
            yield attr_name
        else:
            yield attr_name, attr_value


def get_declared_attribute(obj, attribute_name):
    try:
        if attribute_name in vars(obj):
            return getattr(obj, attribute_name)
    except TypeError:
        pass
    raise ValueError("no attribute named %s" % attribute_name)


def get_declared_attributes(obj, only_names=False):
    """返回对象或类中定义的所有方法和属性"""
    for attr_name, attr_value in vars(obj).iteritems():
        if only_names:
            yield attr_name
        else:
            yield attr_name, attr_value
