# coding: utf8

__all__ = ["EnumDescriptor", "EnumMetaClass", "BaseEnum", "EnumBuilder"]
__authors__ = ["Tim Chow"]

from ..reflect import get_declared_field


class EnumDescriptor(object):
    def __init__(self, present, priority=0):
        self._present = present
        self._priority = priority

    def __get__(self, obj, obj_typ=None):
        return self._present

    def __set__(self, obj, value):
        raise RuntimeError("permission denied")

    def __delete__(self, obj):
        raise RuntimeError("permission denied")

    @property
    def present(self):
        return self._present

    @property
    def priority(self):
        return self._priority


class EnumMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        presents = []
        for attr_name, attr_value in attrs.items():
            if not isinstance(attr_value, EnumDescriptor):
                continue
            for present in presents:
                if attr_value.present == present:
                    raise ValueError("duplicated present")
            else:
                presents.append(attr_value.present)
        return super(EnumMetaClass, mcs).__new__(mcs, name, bases, attrs)


class BaseEnum(object):
    __metaclass__ = EnumMetaClass

    def compare(self, present1, present2):
        descriptor1 = None
        descriptor2 = None
        for field_name, field_value in \
                get_declared_field(self.__class__, EnumDescriptor):
            if field_value.present == present1:
                descriptor1 = field_value
            elif field_value.present == present2:
                descriptor2 = field_value
        if descriptor1 is None:
            raise ValueError("%s is absent" % present1)
        if descriptor2 is None:
            raise ValueError("%s is absent" % present2)

        if descriptor1.priority > descriptor2.priority:
            return 1
        if descriptor1.priority == descriptor2.priority:
            return 0
        return -1

    def is_present(self, present):
        for enum_value, descriptor in get_declared_field(
                self.__class__,
                EnumDescriptor):
            if present == descriptor.present:
                return True
        else:
            return False

    def iter_values(self):
        for _, descriptor in \
                get_declared_field(self.__class__,
                                   EnumDescriptor):
            yield descriptor.present


class EnumBuilder(object):
    def __init__(self):
        self._name = None
        self._enum_values = []

    def with_name(self, name):
        self._name = name
        return self

    def with_enum_value(self, enum_value,
                        present, priority=0):
        self._enum_values.append(
            (enum_value, (present, priority))
        )
        return self

    def build(self):
        if not self._name or not self._enum_values:
            return None
        return type(
            self._name,
            (BaseEnum, ),
            dict(
                [(enum_value, EnumDescriptor(*args))
                 for enum_value, args in self._enum_values
                 ]
            )
        )()
