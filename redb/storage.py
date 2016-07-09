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


class JSONStorage(object):
    implements(IStorage)

    extension = 'json'

    def __init__(self, filename ):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def read(self):
        with open( self.filename, 'r' ) as f:
            data = f.read()
            return json.loads(data)

    def write(self, data):
        if data is None:
            return False

        with open( self.filename, 'w' ) as f:
            f.write( json.dumps(data) )

        return True
