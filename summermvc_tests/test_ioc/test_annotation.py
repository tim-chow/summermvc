import unittest

from summermvc.decorator import *


@component(name="test-class", is_singleton=False)
class TestComponentWithArgs(object):
    pass


@component
class TestComponentWithoutArgs(object):
    pass


@component
def test_func():
    pass


class TestAnnotation(unittest.TestCase):
    def test_component_with_args(self):
        self.assertTrue(is_component_present(TestComponentWithArgs))
        args, kwargs = get_component(TestComponentWithArgs)
        self.assertEqual(len(args), 0)
        self.assertEqual(kwargs["name"], "test-class")
        self.assertFalse(kwargs["is_singleton"])

    def test_component_without_args(self):
        self.assertTrue(is_component_present(TestComponentWithoutArgs))
        args, kwargs = get_component(TestComponentWithoutArgs)
        self.assertEqual(len(args), 0)
        self.assertEqual(len(kwargs), 0)

    def test_component_for_func(self):
        self.assertFalse(is_component_present(test_func))
