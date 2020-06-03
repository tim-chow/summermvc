import unittest

from summermvc.decorator import *
from summermvc import BeanFactory


@controller
class TestController(object):
    @auto_wired
    def test_service(self):
        pass


@service
class TestService(object):
    @auto_wired
    def test_dao(self):
        pass


@repository
class TestDao(object):
    pass


@component("test-class-for-circular-dependency")
class TestClassForCircularDependency(object):
    @auto_wired("test-class-for-circular-dependency")
    def circular_dependency(self):
        pass


class TestBeanFactory(unittest.TestCase):
    def test_get_bean(self):
        bean_classes = [TestController, TestService, TestDao]
        factory = BeanFactory(bean_classes)
        test_controller = factory.get_bean("TestController")
        self.assertIs(test_controller, factory.get_bean("TestController"))
        test_service = factory.get_bean("TestService")
        self.assertIs(test_controller.test_service, test_service)
        test_dao = factory.get_bean("TestDao")
        self.assertIs(test_service.test_dao, test_dao)

    def test_circular_dependency(self):
        bean_classes = [TestClassForCircularDependency]
        factory = BeanFactory(bean_classes)
        obj = factory.get_bean("test-class-for-circular-dependency")
        self.assertIs(obj.circular_dependency, obj)
