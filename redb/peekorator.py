"""
Generic Peekorator, modeled after next(), for "looking into the future" of a generator/iterator.

ACKNOWLEDGEMENTS
-----------------
"plof" for the name: http://stackoverflow.com/a/10576559/589362
Ned Batchelder for the buffered __peek__: http://stackoverflow.com/a/1517965/589362
"""

def peek(peekorator, n=None, default=None):
    """
    next()-like function to be used with a Peekorator

    :param peekorator: Peekorator to use
    :param n: Number of items to look ahead
    :type n: int
    :param default: If the iterator is exhausted then a default is given
    """
    try:
        return peekorator.__peek__(n=n)
    except StopIteration:
        if default is not None:
            return default
        else:
            raise


class Peekorator(object):
    """
    Wrap a generator (or iterator) and allow the ability to peek at the next element in a lazy fashion.  If
    the user never uses peek(), then the only cost over a regular generator is the proxied function call.
    """

    def __init__(self, generator):
        self.generator = generator
        self._peek_buffer = []

    def __peek__(self, n=0):
        """
        Return the peeked element for the generator

        :param n: Integer of how many iterations into the future to peek
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
            return self._peek_buffer.pop(0)
        else:
            return next(self.generator)

    # Allow Python 2/3
    next = __next__

    def __iter__(self):
        """
        Allow the Peakorator to be used as a regular iterable
        """
        return self
