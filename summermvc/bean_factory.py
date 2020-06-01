# coding: utf8

__all__ = ["BeanFactory"]
__authors__ = ["Tim Chow"]

import threading
import logging

from .exception import *
from .bean import *
from .decorator import *
from .reflect import get_declared_methods

LOGGER = logging.getLogger(__name__)


class BeanFactory(object):
    def __init__(self, bean_classes):
        self._lock = threading.RLock()
        self._name_to_bean = {}
        self._name_to_obj = {}
        self._before_advice = {}
        self._around_advice = {}
        self._after_returning_advice = {}
        self._after_throwing_advice = {}
        self._after_advice = {}

        for bean_class in bean_classes:
            bean = Bean.from_bean_class(bean_class)
            if bean.name in self._name_to_bean:
                raise DuplicatedBeanNameError("bean %s duplicated" % bean.name)
            self._name_to_bean[bean.name] = bean
            self.__initialize_advices(bean)

        self.__weave(bean_classes)

    @property
    def wrapper(self):
        from .wrapper import wrapper
        return wrapper

    def __initialize_advices(self, bean):
        order = get_aspect(bean.cls)
        if order is None:
            return

        for attr_name, attr_value in get_declared_methods(bean.cls):
            point_cut = get_before(attr_value)
            if point_cut is not None:
                self._before_advice.setdefault(point_cut, []) \
                    .append((bean.name, attr_name, order))

            point_cut = get_around(attr_value)
            if point_cut is not None:
                self._around_advice.setdefault(point_cut, []) \
                    .append((bean.name, attr_name, order))

            point_cut = get_after_throwing(attr_value)
            if point_cut is not None:
                self._after_throwing_advice.setdefault(point_cut, []) \
                    .append((bean.name, attr_name, order))

            point_cut = get_after_returning(attr_value)
            if point_cut is not None:
                self._after_returning_advice.setdefault(point_cut, []) \
                    .append((bean.name, attr_name, order))

            point_cut = get_after(attr_value)
            if point_cut is not None:
                self._after_advice.setdefault(point_cut, []) \
                    .append((bean.name, attr_name, order))

    def __weave(self, bean_classes):
        generate_advices = """\
import re

{{ADVICE_TYPE}}s = []
for point_cut, advices in self._{{ADVICE_TYPE}}.iteritems():
    if not re.match(
            point_cut.rstrip("$")+"$",
            "%s %s" % (class_name, attr_name)):
        continue
    for advice in advices:
        {{ADVICE_TYPE}}s.append((getattr(self.get_bean(advice[0]), advice[1]), advice[2]))
{{ADVICE_TYPE}}s = [advice[0] for advice in sorted({{ADVICE_TYPE}}s, key=lambda t: t[1], reverse=True)]
"""

        for bean_class in bean_classes:
            class_name = bean_class.__name__
            for attr_name, attr in get_declared_methods(bean_class):
                _locals = locals()
                for advice_type in ["before_advice",
                                    "around_advice",
                                    "after_returning_advice",
                                    "after_throwing_advice",
                                    "after_advice"]:
                    exec(generate_advices.replace("{{ADVICE_TYPE}}", advice_type),
                         globals(), _locals)
                before_advices = _locals["before_advices"]
                around_advices = _locals["around_advices"]
                after_returning_advices = _locals["after_returning_advices"]
                after_throwing_advices = _locals["after_throwing_advices"]
                after_advices = _locals["after_advices"]
                if before_advices or \
                        around_advices or \
                        after_returning_advices or \
                        after_throwing_advices or \
                        after_advices:
                    setattr(
                        bean_class,
                        attr_name,
                        self.wrapper(
                            before_advices,
                            around_advices,
                            after_returning_advices,
                            after_throwing_advices,
                            after_advices)(attr))

    def get_bean(self, name):
        return self.__get_bean(name, {}, {})

    def __get_bean(self, name, creating, created):
        if name in self._name_to_obj:
            return self._name_to_obj[name]
        if name not in self._name_to_bean:
            raise BeanNotFoundError("bean %s not found" % name)
        bean = self._name_to_bean[name]

        # 如果是单例 bean
        if bean.is_singleton:
            with self._lock:
                if name in self._name_to_obj:
                    return self._name_to_obj[name]
                # 创建 bean 实例
                obj = bean.cls()
                # 处理依赖
                self.__process_dependency(obj, bean, creating, created)
                # 将单例 bean 缓存起来
                self._name_to_obj[name] = obj
                # 调用 post_construct
                bean.post_construct(obj)
                return obj
        obj = bean.cls()
        self.__process_dependency(obj, bean, creating, created)
        bean.post_construct(obj)
        return obj

    def __process_dependency(self, obj, bean, creating, created):
        creating[bean.name] = obj
        for attr_name, attr_value in bean.properties.iteritems():
            setattr(obj, attr_name, attr_value)
        for attr_name, dependency_bean_name in bean.auto_wired.iteritems():
            # 循环引用
            if dependency_bean_name in creating:
                setattr(obj, attr_name, creating[dependency_bean_name])
                continue
            if dependency_bean_name in created:
                setattr(obj, attr_name, created[dependency_bean_name])
                continue
            setattr(obj,
                    attr_name,
                    self.__get_bean(dependency_bean_name, creating, created))
        del creating[bean.name]
        created[bean.name] = obj

    def destroy(self):
        for name in self._name_to_obj:
            obj = self._name_to_obj[name]
            bean = self._name_to_bean[name]
            try:
                bean.pre_destroy(obj)
            except:
                LOGGER.error("fail to call pre destroy", exc_info=True)

    def iter_beans(self):
        for item in self._name_to_bean.iteritems():
            yield item
