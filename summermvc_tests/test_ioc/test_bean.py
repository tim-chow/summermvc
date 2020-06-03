import unittest

from summermvc.decorator import *
from summermvc import Bean, is_bean_class


@component
class BeanForTest(object):
    @post_construct
    def post_construct(self):
        pass

    @pre_destroy
    def pre_destroy(self):
        pass

    @value("value")
    def value(self):
        pass

    @auto_wired
    def auto_wired(self):
        pass


class TestBean(unittest.TestCase):
    def test_bean(self):
        self.assertTrue(is_bean_class(BeanForTest))
        bean_object = Bean.from_bean_class(BeanForTest)
        self.assertEqual(bean_object.post_construct, BeanForTest.post_construct)
        self.assertEqual(bean_object.pre_destroy, BeanForTest.pre_destroy)
        self.assertEqual(bean_object.properties["value"], "value")
        self.assertEqual(bean_object.auto_wired["auto_wired"], "AutoWired")
