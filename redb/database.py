from zope.interface import Interface, Attribute, implements
import datetime as dt
from collections import OrderedDict
import os

from .storage import JSONStorage
from .table import Table
from .fields import Field

class IDatabase( Interface ):

    tables   = Attribute("the dict of tables")

class Database(object):
    implements(IDatabase)

    def __init__( self, tables=[], *args, **kw ):

        self._tables = OrderedDict()
        for table in tables:
            self._tables[table.name] = table

        self._storage_type = kw.pop('storage', JSONStorage)
        self._root_dir = kw.pop('root_dir', '.')

    @property
    def tables(self):
        return self._tables.values()

    def get_filename(self, table):
        """
        allow tables to specify their own filename or use
        storage extension default
        """
        ext = self._storage_type.extension
        filename = table.filename or "{}.{}".format(table.name,ext)
        return os.path.join( self._root_dir, filename )

    def get_storage(self, table):
        """
        allow tables to specify their own storage or use
        database default
        """
        return table.storage or self._storage_type

    def load(self):
        """
        load the data for each table
        """
        records = OrderedDict()

        for table in self.tables:
            storage = self.get_storage(table)
            for record in storage.read():
                instance = table.__class__(**record)
                records[ instance.pk ] = instance
