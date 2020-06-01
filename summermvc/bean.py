# coding: utf8

__all__ = ["Bean",
           "is_bean_class",
           "component_scan_package",
           "component_scan_path"]
__authors__ = ["Tim Chow"]

from types import ModuleType
import __builtin__

from .decorator import *
from .scanner import *
from .reflect import *
from .field import *


def is_bean_class(cls, mod=None):
    if not is_component_present(cls):
        return False
    if not isinstance(mod, ModuleType):
        return True
    return cls.__module__ == mod.__name__


def component_scan_package(*packages):
    bean_classes = set()
    for mod in scan_package(*packages):
        for attr_name, attr_value in get_declared_attributes(mod):
            if is_builtin_present(attr_value):
                setattr(__builtin__, attr_name, attr_value)
            if not is_bean_class(attr_value, mod):
                continue
            bean_classes.add(attr_value)
    return bean_classes


def component_scan_path(*paths):
    bean_classes = set()
    for mod in scan_path(*paths):
        for attr_name, attr_value in get_declared_attributes(mod):
            if is_builtin_present(attr_value):
                setattr(__builtin__, attr_name, attr_value)
            if not is_bean_class(attr_value, mod):
                continue
            bean_classes.add(attr_value)
    return bean_classes


class Bean(object):
    @classmethod
    def from_bean_class(cls, bean_class):
        args, kwargs = get_component(bean_class)
        bean_object = Bean()
        bean_object.__extract_attribute(
            bean_class,
            *args,
            **kwargs)
        return bean_object

    def __extract_attribute(self, bean_class, name=None, is_singleton=True):
        self._cls = bean_class
        self._name = name or self._cls.__name__
        self._is_singleton = is_singleton

        self._post_construct = lambda *a, **kw: None
        self._pre_destroy = lambda *a, **kw: None
        self._auto_wired = {}
        self._properties = {}
        for attr_name, attr_value in get_declared_methods(self._cls):
            if is_post_construct_present(attr_value):
                self._post_construct = attr_value
            if is_pre_destroy_present(attr_value):
                self._pre_destroy = attr_value
            if is_auto_wired_present(attr_value):
                self._auto_wired[attr_name] = get_auto_wired(attr_value)
            if is_value_present(attr_value):
                self._properties[attr_name] = get_value(attr_value)

        for attr_name, attr_value in get_declared_fields(self._cls):
            if isinstance(attr_value, AutoWiredField):
                self._auto_wired[attr_name] = attr_value.auto_wired or \
                    "".join(w.capitalize() for w in attr_name.split("_"))
            if isinstance(attr_value, ValueField):
                self._properties[attr_name] = attr_value.value

    @property
    def cls(self):
        return self._cls

    @property
    def name(self):
        return self._name

    @property
    def is_singleton(self):
        return self._is_singleton

    @property
    def post_construct(self):
        return self._post_construct

    @property
    def pre_destroy(self):
        return self._pre_destroy

    @property
    def auto_wired(self):
        return self._auto_wired

    @property
    def properties(self):
        return self._properties
