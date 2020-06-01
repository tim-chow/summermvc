# coding: utf8

__all__ = ["component", "repository", "service", "controller", "configuration",
           "is_component_present", "is_repository_present",
           "is_configuration_present", "is_service_present", "is_controller_present",
           "get_component", "get_repository", "get_service", "get_controller",
           "get_configuration",

           "post_construct", "pre_destroy",
           "is_post_construct_present", "is_pre_destroy_present",

           "value", "auto_wired",
           "is_value_present", "is_auto_wired_present",
           "get_value", "get_auto_wired"]
__authors__ = ["Tim Chow"]

import inspect
import types

from ..reflect import get_declared_fields


# 该装饰器只能装饰类
def component(*args, **kwargs):
    # 不带参的装饰器
    if len(args) == 1 and \
            inspect.isclass(args[0]) and \
            not kwargs:
        cls = args[0]
        setattr(cls, "__bean_class__", True)
        setattr(cls, "__bean_args__", tuple())
        setattr(cls, "__bean_kwargs__", dict())
        return cls

    # 带参的装饰器
    def _inner(clazz):
        if not inspect.isclass(clazz):
            raise RuntimeError("class expected")
        setattr(clazz, "__bean_class__", True)
        setattr(clazz, "__bean_args__", args)
        setattr(clazz, "__bean_kwargs__", kwargs)
        return clazz
    return _inner


def is_component_present(cls):
    if not inspect.isclass(cls):
        return False

    attributes = list(get_declared_fields(cls, only_names=True))
    return "__bean_class__" in attributes and \
        getattr(cls, "__bean_class__") is True and \
        "__bean_args__" in attributes and \
        isinstance(getattr(cls, "__bean_args__"), tuple) and \
        "__bean_kwargs__" in attributes and \
        isinstance(getattr(cls, "__bean_kwargs__"), dict)


def get_component(cls, default=None):
    if not is_component_present(cls):
        return default
    return getattr(cls, "__bean_args__"), getattr(cls, "__bean_kwargs__")


repository = component
service = component
controller = component
configuration = component

is_repository_present = is_component_present
is_service_present = is_component_present
is_controller_present = is_component_present
is_configuration_present = is_component_present

get_repository = get_component
get_service = get_component
get_controller = get_component
get_configuration = get_component


def post_construct(f):
    if not isinstance(f, types.FunctionType):
        raise RuntimeError("function expected")
    setattr(f, "__bean_post_construct__", True)
    return f


def is_post_construct_present(f):
    return "__bean_post_construct__" in get_declared_fields(f, only_names=True) and \
        getattr(f, "__bean_post_construct__") is True


def pre_destroy(f):
    if not isinstance(f, types.FunctionType):
        raise RuntimeError("function expected")
    setattr(f, "__bean_pre_destroy__", True)
    return f


def is_pre_destroy_present(f):
    return "__bean_pre_destroy__" in get_declared_fields(f, only_names=True) and \
        getattr(f, "__bean_pre_destroy__") is True


def value(v):
    def _inner(f):
        if not isinstance(f, types.FunctionType):
            raise RuntimeError("function expected")
        setattr(f, "__bean_value__", v)
        return f
    return _inner


def is_value_present(f):
    return "__bean_value__" in get_declared_fields(f, only_names=True)


def get_value(f, default=None):
    if not is_value_present(f):
        return default
    return getattr(f, "__bean_value__")


def auto_wired(a):
    # 带参的情况
    if isinstance(a, basestring):
        def _inner(f):
            if not isinstance(f, types.FunctionType):
                raise RuntimeError("function expected")
            setattr(f, "__bean_auto_wired__", a)
            return f
        return _inner

    # 无参的情况
    if isinstance(a, types.FunctionType):
        setattr(
            a,
            "__bean_auto_wired__",
            "".join(w.capitalize() for w in a.__name__.split("_"))
        )
        return a

    raise RuntimeError("invalid usage")


def get_auto_wired(f):
    if "__bean_auto_wired__" not in get_declared_fields(f, only_names=True):
        return None
    attr_value = getattr(f, "__bean_auto_wired__")
    if not isinstance(attr_value, basestring):
        return None
    return attr_value


def is_auto_wired_present(f):
    return get_auto_wired(f) is not None
