import unittest

from summermvc.decorator import *


@aspect(1)
class TestAspectClass(object):
    @before(r".* .*")
    def before(self):
        pass

    @around(r".* .*")
    def around(self):
        pass

    @after_returning(r".* .*")
    def after_returning(self):
        pass

    @after_throwing(r".* .*")
    def after_throwing(self):
        pass

    @after(r".* .*")
    def after(self):
        pass


class TestAnnotation(unittest.TestCase):
    def test_annotation(self):
        self.assertTrue(is_aspect_present(TestAspectClass))
        self.assertTrue(is_before_present(getattr(TestAspectClass, "before")))
        self.assertTrue(is_around_present(getattr(TestAspectClass, "around")))
        self.assertTrue(is_after_returning_present(getattr(TestAspectClass, "after_returning")))
        self.assertTrue(is_after_throwing_present(getattr(TestAspectClass, "after_throwing")))
        self.assertTrue(is_after_present(getattr(TestAspectClass, "after")))
