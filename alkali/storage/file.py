import os
import types
from contextlib import contextmanager
#from zope.interface import Interface, Attribute, implements
import json
import csv

from alkali.peekorator import Peekorator
from . import Storage

import logging
logger = logging.getLogger(__name__)

try:
    import fcntl
except ImportError: # pragma: nocover
    # HACK windows doesn't have fcntl module so fake it out
    class fcntl:
        LOCK_EX = 0
        LOCK_NB = 0
        LOCK_UN = 0

        @staticmethod
        def flock(*args, **kw):
            return True


class FileAlreadyLocked(Exception):
    """
    the exception that is thrown when a storage instance tries
    and fails to lock its data file
    """
    pass

class FileStorage(Storage):
    """
    this helper class determines the on-disk representation of the database. it
    could write out objects as json or plain txt or binary, that's up to
    the implementation and should be transparent to any models/database.
    """
    #implements(IStorage)
    extension = 'raw'

    def __init__(self, filename=None, *args, **kw ):
        self._fhandle = None
        self.filename = filename # property

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

        if isinstance(filename, str):
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
        # THINK should this yield blocks of data?
        # https://github.com/kashifrazzaqui/json-streamer
        # https://pypi.org/project/ijson/
        self._fhandle.seek(0)
        return self._fhandle.read()

    def _write(self, iterator):
        """
        helper function that just writes a file if data is not None
        """
        if iterator is None:
            return False

        self._fhandle.seek(0)

        for data in iterator:
            self._fhandle.write(str(data))

        self._fhandle.truncate()
        self._fhandle.flush()
        return True

    def write(self, model_class, iterator):
        return self._write(iterator)
