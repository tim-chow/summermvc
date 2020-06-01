# coding: utf8

__all__ = ["request_mapping", "is_request_mapping_present", "get_request_mapping",
           "exception_handler", "is_exception_handler_present", "get_exception_handler",
           "rest_controller", "is_rest_controller_present"]
__authors__ = ["Tim Chow"]

import types
import inspect

from ..reflect import *
from .component import component
from ..utility import is_tornado_installed


# request_mapping 既可以装饰类，也可以装饰方法
def request_mapping(uri, method=None, consumes=None, produce=None):
    def _inner(f):
        if isinstance(f, types.FunctionType):
            setattr(f,
                    "__mvc_args__",
                    {
                        "uri": uri,
                        "method": method,
                        "consumes": isinstance(consumes, basestring) and [consumes] or (consumes or []),
                        "produce": produce,
                        "arg_spec": inspect.getargspec(f)
                    }
                    )
        elif inspect.isclass(f):
            setattr(f, "__mvc_args__", {"uri": uri})
        return f
    return _inner


def get_request_mapping(obj):
    if "__mvc_args__" not in get_declared_fields(obj, only_names=True):
        return None
    attr_value = getattr(obj, "__mvc_args__")
    if not isinstance(attr_value, dict) or "uri" not in attr_value:
        return None
    return attr_value


def is_request_mapping_present(obj):
    return get_request_mapping(obj) is not None


def exception_handler(uri, *exceptions):
    if not isinstance(uri, basestring) or not uri:
        raise RuntimeError("invalid uri")
    for exc in exceptions:
        if not inspect.isclass(exc) or not issubclass(exc, BaseException):
            raise RuntimeError("exception expected")

    def _inner(f):
        if not isinstance(f, types.FunctionType):
            raise RuntimeError("function expected")
        setattr(
            f,
            "__mvc_exception_handler__",
            {"uri": uri,
             "exceptions": exceptions,
             "arg_spec": inspect.getargspec(f)
            })
        return f
    return _inner


def get_exception_handler(f, default=None):
    if not isinstance(f, types.MethodType):
        raise RuntimeError("method expected")
    annotation = getattr(f, "__mvc_exception_handler__", None)
    if annotation is None or \
            not isinstance(annotation, dict) or \
            "uri" not in annotation or \
            "exceptions" not in annotation or \
            "arg_spec" not in annotation:
        return default
    return annotation


def is_exception_handler_present(f):
    return get_exception_handler(f, None) is not None


def _create_rest_controller(key):
    def rest_controller(*outer_args, **outer_kwargs):
        returning = component(*outer_args, **outer_kwargs)
        if inspect.isclass(returning):
            setattr(returning, key, True)
            return returning

        def _inner(*inner_args, **inner_kwargs):
            cls = returning(*inner_args, **inner_kwargs)
            setattr(cls, key, True)
            return cls
        return _inner
    return rest_controller


rest_controller = _create_rest_controller("__rest_controller__")
if is_tornado_installed:
    __all__.append("tornado_rest_controller")
    tornado_rest_controller = \
        _create_rest_controller("__tornado_rest_controller__")


def _create_is_rest_controller_present(key):
    def is_rest_controller_present(cls):
        try:
            return get_declared_attribute(
                cls,
                key) is True
        except ValueError:
            return False
    return is_rest_controller_present


is_rest_controller_present = \
    _create_is_rest_controller_present(
        "__rest_controller__")
if is_tornado_installed:
    __all__.append("is_tornado_rest_controller_present")
    is_tornado_rest_controller_present = \
        _create_is_rest_controller_present(
            "__tornado_rest_controller__")

