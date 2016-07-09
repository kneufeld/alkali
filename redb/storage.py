from zope.interface import Interface, Attribute, implements
import json

class IStorage( Interface ):

    extension   = Attribute("class level attr of desired filename extension. eg. json")
    filename    = Attribute("file we'll be writing too")

    def read():
        """
        return a dict
        up to implementer but likely you want to read filename
        """

    def write( data ):
        """
        accept a dict
        up to implementer but likely you want to write out to filename
        """

class Storage(object):
    """
    this class determines the on-disk representation of the database. it
    could write out objects as json or plain txt or binary, that's up to
    the implementation and should be transparent to any models.
    """

    def __init__(self, filename ):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def _read(self):
        with open( self.filename, 'r' ) as f:
            return f.read()

    def _write(self, data):
        if data is None:
            return False

        with open( self.filename, 'w' ) as f:
            f.write( bytes(data) )

        return True

class TextStorage(Storage):
    """
    just a plain reader/writer, no parsing
    """
    implements(IStorage)

    extension = 'txt'

    def read(self):
        return self._read()

    def write(self, data):
        if data is None:
            return False

        return self._write( bytes(data) )


class JSONStorage(Storage):
    implements(IStorage)

    extension = 'json'

    def read(self):
        data = self._read()
        return json.loads(data)

    def write(self, data):
        if data is None:
            return False

        data = json.dumps(data)
        return self._write(data)
