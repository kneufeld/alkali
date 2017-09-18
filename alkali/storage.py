import os
import types
import fcntl
from contextlib import contextmanager
from zope.interface import Interface, Attribute, implements
import json
import csv

from .peekorator import Peekorator

import logging
logger = logging.getLogger(__name__)


class FileAlreadyLocked(Exception):
    """
    the exception that is thrown when a storage instance tries
    and fails to lock its data file
    """
    pass


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

    def __init__(self, filename=None, *args, **kw ):
        self._fhandle = None
        self.filename = filename

    def __del__(self):
        self.unlock()

    @property
    def filename(self):
        if self._fhandle is None:
            return None

        return self._fhandle.name

    @filename.setter
    def filename(self, filename):
        """
        when setting the filename, immediately open and lock the file handle
        """
        self.unlock()

        if filename is None:
            if self._fhandle:
                self._fhandle.close()
                self._fhandle = None
            return

        if isinstance(filename, types.StringTypes):
            filename = os.path.expanduser(filename)

            if os.path.exists(filename):
                assert os.path.isfile(filename)
                self._fhandle = open(filename, 'r+')
            else:
                self._fhandle = open(filename, 'w+')

        else: # assuming file type
            self._fhandle = filename

        self.lock()

    def lock(self):
        if not self._fhandle:
            return

        try:
            fcntl.flock(self._fhandle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise FileAlreadyLocked("can't lock: {}".format(self.filename))

    def unlock(self):
        if not self._fhandle:
            return

        # I don't think this can ever fail
        fcntl.flock(self._fhandle, fcntl.LOCK_UN)

    def read(self, model_class):
        """
        helper function that just reads a file
        """
        self._fhandle.seek(0)
        return self._fhandle.read()

    def _write(self, iterator):
        """
        helper function that just writes a file if
        data is not None
        """
        if iterator is None:
            return False

        self._fhandle.seek(0)

        for data in iterator:
            self._fhandle.write( bytes(data) )

        self._fhandle.truncate()
        self._fhandle.flush()
        return True

    def write(self, iterator):
        return self._write(iterator)


class JSONStorage(FileStorage):
    """
    save models in json format
    """
    extension = 'json'

    def read(self, model_class):
        data = super(JSONStorage, self).read(model_class)

        if not data:
            return

        for elem in json.loads(data):
            yield elem

    def write(self, iterator):

        if iterator is None:
            return False

        f = self._fhandle
        f.seek(0)

        f.write('[\n')

        _peek = Peekorator(iter(iterator))
        for e in _peek:
            data = json.dumps(e.dict)
            f.write(data)

            if not _peek.is_last():
                f.write(',\n')

        f.write('\n]')

        # since the file may shrink (we've deleted records) then
        # we must truncate the file at our current position to avoid
        # stale data being present on the next load
        f.truncate()
        f.flush()

        return True


class CSVStorage(FileStorage):
    """
    load models in csv format

    first line assumed to be column headers (aka: field names)

    use `remap_fieldnames` to change column headers into model field names
    """
    extension = 'csv'

    def read(self, model_class):
        self._fhandle.seek(0)
        reader = csv.DictReader(self._fhandle)

        for row in reader:
            row = self.remap_fieldnames(model_class, row)
            yield model_class(**row)

    def remap_fieldnames(self, model_class, row):
        """
        example of remap_fieldnames that could be defined
        in derived class or as a stand-alone function.

        warning: make sure your header row that contains field
        names has no spaces in it

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

        f = self._fhandle
        f.seek(0)

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

        f.truncate()
        return True
