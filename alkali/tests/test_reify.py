import unittest

from alkali.reify import reify

class Class:

    @reify
    def x(self):
        return list(range(5))

class TestReify( unittest.TestCase ):

    def test_1(self):
        Class.x # for test coverage

        c = Class()
        self.assertTrue(isinstance(c.x, list))
