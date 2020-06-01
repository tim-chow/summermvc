# coding: utf8

__all__ = ["ApplicationContext",
           "BasePackageApplicationContext",
           "FilePathApplicationContext"]
__authors__ = ["Tim Chow"]

from .bean import *
from .exception import *
from .bean_factory import BeanFactory
from .utility import is_tornado_installed


class ApplicationContext(BeanFactory):
    def __init__(self, bean_classes):
        BeanFactory.__init__(self, bean_classes)

        for name in self._name_to_bean:
            bean = self._name_to_bean[name]
            if bean.is_singleton:
                self.get_bean(bean.name)

    def add_bean(self, bean_class, mod=None):
        if not is_bean_class(bean_class, mod):
            raise UnavailableBeanClassError("bean expected")
        bean = Bean.from_bean_class(bean_class)
        if bean.name in self._name_to_bean:
            raise DuplicatedBeanNameError("duplicated bean name")
        self._name_to_bean[bean.name] = bean
        if bean.is_singleton:
            self.get_bean(bean.name)

    def close(self):
        self.destroy()

    def __del__(self):
        try:
            self.close()
        except AttributeError:
            pass


class BasePackageApplicationContext(ApplicationContext):
    def __init__(self, *packages):
        ApplicationContext.__init__(
            self,
            component_scan_package(*packages))


class FilePathApplicationContext(ApplicationContext):
    def __init__(self, *paths):
        ApplicationContext.__init__(
            self,
            component_scan_path(*paths))


if is_tornado_installed:
    __all__.extend([
        "TornadoApplicationContext",
        "TornadoBasePackageApplicationContext",
        "TornadoFilePathApplicationContext"])


    class TornadoApplicationContext(ApplicationContext):
        @property
        def wrapper(self):
            from .wrapper import tornado_wrapper
            return tornado_wrapper


    class TornadoBasePackageApplicationContext(
            TornadoApplicationContext):
        def __init__(self, *packages):
            TornadoApplicationContext.__init__(
                self,
                component_scan_package(*packages))


    class TornadoFilePathApplicationContext(
            TornadoApplicationContext):
        def __init__(self, *paths):
            TornadoApplicationContext.__init__(
                self,
                component_scan_path(*paths))

