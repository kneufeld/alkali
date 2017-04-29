import os
from zope.interface import Interface, Attribute, implements
import json
import csv

from .peekorator import Peekorator

import logging
logger = logging.getLogger(__name__)

class IStorage( Interface ):

    extension = Attribute("class level attr of desired filename extension. eg. json")

    def read(model_class):
        """
        yield (or return a list) of instantiated model_class objects or dicts
        up to implementer but likely you want to read filename
        """

    def write(iterator):
        """
        accept an iterator that yields elements
        up to implementer but likely you want to write out to filename
        """


class Storage(object):
    """
    helper base class for the Storage object hierarchy
    """

    def __init__(self, *args, **kw ):
        pass

    @property
    def _name(self):
        return self.__class__.__name__


class FileStorage(Storage):
    """
    this helper class determines the on-disk representation of the database. it
    could write out objects as json or plain txt or binary, that's up to
    the implementation and should be transparent to any models/database.
    """
    implements(IStorage)
    extension = 'raw'

    def __init__(self, filename, *args, **kw ):
        self._filename = os.path.expanduser(filename)

    @property
    def filename(self):
        return self._filename

    def read(self, model_class):
        """
        helper function that does just reads a file
        """
        with open( self.filename, 'r' ) as f:
            return f.read()

    def _write(self, iterator):
        """
        helper function that does just writes a file if
        data is not None
        """
        if iterator is None:
            return False

        with open( self.filename, 'w' ) as f:
            for data in iterator:
                f.write( bytes(data) )

        return True

    def write(self, iterator):
        return self._write(iterator)


class JSONStorage(FileStorage):
    """
    save models in json format
    """
    extension = 'json'

    def read(self, model_class):
        data = super(JSONStorage,self).read(model_class)

        if not data:
            return

        for elem in json.loads(data):
            yield elem

    def write(self, iterator):

        if iterator is None:
            return False

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


class CSVStorage(FileStorage):
    """
    load models in csv format

    first line assumed to be column headers (aka: field names)

    use `remap_fieldnames` to change column headers into model field names
    """
    extension = 'csv'

    def read(self, model_class):
        with open( self.filename, 'r' ) as f:
            reader = csv.DictReader(f)

            for row in reader:
                row = self.remap_fieldnames(model_class, row)
                yield model_class(**row)

    def remap_fieldnames(self, model_class, row):
        """
        example of remap_fieldnames that could be defined
        in derived class or as a stand-alone function.

        ::

            def remap_fieldnames(self, model_class, row):
                fields = model_class.Meta.fields.keys()

                for k in row.keys():
                    results_key = k.lower().replace(' ', '_')

                    if results_key not in fields:
                        if k == 'Some Wierd Name':
                            results_key = 'good_name'
                        else:
                            raise RuntimeError( "unknown field: {}".format(k) )

                    row[results_key] = row.pop(k)

                return row
        """
        return row

    def write(self, iterator):
        """
        warning: if ``remap_fieldnames`` changes names then saved file
        will have a different header line than original file
        """
        if iterator is None:
            return False

        with open( self.filename, 'w' ) as f:
            _peek = Peekorator(iter(iterator))
            writer = None

            for e in _peek:
                if _peek.is_first():
                    fieldnames = e.Meta.fields.keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(e.dict)
                else:
                    writer.writerow(e.dict)

        return True
