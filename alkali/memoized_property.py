# -*- coding: utf-8 -*-
# from: https://github.com/ytyng/python-memoized-property

import functools

class memoized_property(object):

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):

        if doc is None and fget is not None and hasattr(fget, "__doc__"):
            doc = fget.__doc__

        self.__get = fget
        self.__set = fset
        self.__del = fdel
        self.__doc__ = doc

        if fget is not None:
            self._attr_name = '___'+fget.func_name

    def __get__(self, inst, type=None):
        if inst is None:
            return self

        try:
            return getattr(inst, self._attr_name)
        except AttributeError:
            pass

        result = self.__get(inst)

        if result is not None:
            setattr(inst, self._attr_name, result)

        return result

# note that this decorator ignores **kwargs
def memoize(obj): # pragma: nocover
    cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        try:
            return cache[args]
        except KeyError:
            val = cache[args] = obj(*args, **kwargs)
            return val
    return memoizer
