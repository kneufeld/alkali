"""
from https://gist.github.com/dmckeone/7518335, slightly modified by Kurt Neufeld

Generic Peekorator, modeled after next(), for "looking into the future" of a generator/iterator.

Acknowledgements:

* "plof" for the name: http://stackoverflow.com/a/10576559/589362
* Ned Batchelder for the buffered __peek__: http://stackoverflow.com/a/1517965/589362
"""

class PeekoratorDefault(object): pass

def peek(peekorator, n=0, default=PeekoratorDefault()):
    """
    next()-like function to be used with a Peekorator

    :param peekorator: Peekorator to use
    :param n: Number of items to look ahead
    :type n: int
    :param default: If the iterator is exhausted then a default is
        given, raise StopIteration if not given
    """
    try:
        return peekorator.__peek__(n=n)
    except StopIteration:
        if isinstance(default, PeekoratorDefault):
            raise # StopIteration
        else:
            return default


class Peekorator(object):
    """
    Wrap a generator (or iterator) and allow the ability to peek at the
    next element in a lazy fashion. If the user never uses peek(), then
    the only cost over a regular generator is the proxied function call.
    """

    def __init__(self, generator):
        """
        :param generator: a generator or iterator that will be iterated over
        """
        # a generator is an iterator
        import collections
        if not isinstance( generator, collections.Iterator ):
            generator = iter(generator)

        self.generator = generator
        self._peek_buffer = []

        self._first = None

    def __peek__(self, n=0):
        """
        Return the peeked element for the generator

        :param n: how many iterations into the future to peek
        :type n: int
        """
        while n >= len(self._peek_buffer):
            item = next(self.generator)
            self._peek_buffer.append(item)
        return self._peek_buffer[n]

    # Allow similar syntax to Python 2's next()
    peek = __peek__

    def __next__(self):
        """
        Get the next result from the generator
        """
        if self._peek_buffer:
            ret = self._peek_buffer.pop(0)
        else:
            ret = next(self.generator)

        if self._first is None:
            self._first = True
        elif self._first is True:
            self._first = False

        return ret

    # Allow Python 2/3
    next = __next__

    def __iter__(self):
        """
        Allow the Peakorator to be used as a regular iterable
        """
        return self

    def is_first(self):
        """
        if you just got the first element then return True

        :rtype: bool
        """
        # before first call to next()
        if self._first is None:
            return True

        return self._first

    def is_last(self):
        """
        if you're about to get the last element then return True

        :rtype: bool
        """
        try:
            self.peek()
        except StopIteration:
            return True

        return False
