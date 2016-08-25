from zope.interface import Interface, Attribute, implements
import json

import logging
logger = logging.getLogger(__name__)

class IStorage( Interface ):

    extension   = Attribute("class level attr of desired filename extension. eg. json")
    filename    = Attribute("file we'll be writing too")

    def read(model_class):
        """
        yield (or return a list) of instantiated model_class objects or dicts
        up to implementer but likely you want to read filename
        """

    def write( iterator ):
        """
        accept an iterator that yields elements
        up to implementer but likely you want to write out to filename
        """

class Storage(object):
    """
    this class determines the on-disk representation of the database. it
    could write out objects as json or plain txt or binary, that's up to
    the implementation and should be transparent to any models/database.
    """

    def __init__(self, filename ):
        self._filename = filename

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def filename(self):
        return self._filename

    def _read(self):
        """
        helper function that does just reads a file
        """
        with open( self.filename, 'r' ) as f:
            return f.read()

    def _write(self, data):
        """
        helper function that does just writes a file if
        data is not None
        """
        if data is None:
            return False

        with open( self.filename, 'w' ) as f:
            f.write( bytes(data) )

        return True


class JSONStorage(Storage):
    """
    save models in json format
    """
    implements(IStorage)

    extension = 'json'

    def read(self, model_class):
        data = self._read()
        for elem in json.loads(data):
            yield elem

    def write(self, iterator):
        from peekorator import Peekorator

        with open( self.filename, 'w' ) as f:
            f.write('[\n')

            _peek = Peekorator(iter(iterator))
            for e in _peek:
                data = json.dumps(e.dict)
                f.write(data)

                if not _peek.is_last():
                    f.write(',\n')

            f.write('\n]')

        return True
