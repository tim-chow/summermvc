import unittest
import functools

from summermvc.decorator import *
from summermvc import BeanFactory, return_value


@component
class TestComponent(object):
    def test_before(self):
        return 1

    def test_around(self):
        return 1

    def test_after_returning(self):
        return 1

    def test_after_throwing(self):
        raise RuntimeError()

    def test_after(self):
        return 1


@aspect(1)
@component
class TestAspect(object):
    @before(r"TestComponent test_before")
    def before(self, joint_point):
        return_value(joint_point.proceed() + 1)

    @around(r"TestComponent test_around")
    def around_before(self):
        return functools.partial(self.around_after, 2)

    @staticmethod
    def around_after(n, joint_point, returning, exc_info):
        return_value(n + returning + n + 1)

    @after_returning(r"TestComponent test_after_returning")
    def after_returning(self, returning):
        return_value(returning + 1)

    @after_throwing(r"TestComponent test_after_throwing")
    def after_throwing(self, exc_info):
        return_value(1)

    @after(r"TestComponent test_after")
    def after(self, returning):
        return_value(returning + 1)


class TestAop(unittest.TestCase):
    def test_advice(self):
        bean_classes = [TestComponent, TestAspect]
        factory = BeanFactory(bean_classes)
        test_component = factory.get_bean("TestComponent")
        self.assertEqual(test_component.test_before(), 2)
        self.assertEqual(test_component.test_around(), 6)
        self.assertEqual(test_component.test_after_returning(), 2)
        self.assertEqual(test_component.test_after_throwing(), 1)
        self.assertEqual(test_component.test_after(), 2)
