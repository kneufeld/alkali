import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.database import IDatabase, Database
from redb.table import ITable, Table
from redb.metatable import MetaTable
from redb.storage import JSONStorage
from redb import fields

class MyTable( Table ):
    class Meta:
        ordering = ['int_type','str_type','date_type']

    int_type = fields.IntField()
    str_type = fields.StringField()
    date_type  = fields.DateField()

curr_dir = os.path.dirname( os.path.abspath( __file__ ) )

class TestMetaTable( unittest.TestCase ):

    def test_1(self):
        "verify attributes on class, not instance"

        cls = MyTable
        self.assertTrue( hasattr(cls, '_fields') )
        self.assertTrue( hasattr(cls, 'objects') )
        self.assertTrue( hasattr(cls, 'Meta') )

    def test_2(self):
        "verify attributes on class, not instance"

        class EmptyTable(Table):
            pass

        cls = EmptyTable
        self.assertTrue( hasattr(cls, '_fields') )
        self.assertTrue( hasattr(cls, 'objects') )
        self.assertTrue( hasattr(cls, 'Meta') )

    def test_3(self):
        "verify that Meta.ordering works"

        t = MyTable()
        self.assertEqual( MyTable.Meta.ordering, t.fields.keys() )
