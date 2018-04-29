__title__        = 'alkali'
__version__      = '0.6.0'
__author__       = 'Kurt Neufeld'
__author_email__ = 'kneufeld@burgundywall.com'
__license__      = 'MIT License'
__url__          = 'https://github.com/kneufeld/alkali'
__copyright__    = 'Copyright 2017 Kurt Neufeld'

from .database import Database
from .storage import Storage, FileStorage, JSONStorage
from .manager import Manager
from .model import Model
from .query import Query
from .utils import tznow, tzadd, fromts
from . import fields

class reify(object):
    """ Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.  The following is an example and
    its usage:

    .. doctest::

        >>> from pyramid.decorator import reify

        >>> class Foo(object):
        ...     @reify
        ...     def jammy(self):
        ...         print('jammy called')
        ...         return 1

        >>> f = Foo()
        >>> v = f.jammy
        jammy called
        >>> print(v)
        1
        >>> f.jammy
        1
        >>> # jammy func not called the second time; it replaced itself with 1
        >>> # Note: reassignment is possible
        >>> f.jammy = 2
        >>> f.jammy
        2
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        from functools import update_wrapper
        update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val
