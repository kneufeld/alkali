import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.database import IDatabase, Database
from redb.table import ITable, Table
from redb.storage import JSONStorage
from redb import fields

class MyTable( Table ):
    int_type = fields.IntField()
    str_type = fields.StringField()
    date_type  = fields.DateField()

curr_dir = os.path.dirname( os.path.abspath( __file__ ) )

class TestDatabase( unittest.TestCase ):

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IDatabase, Database) )

        db = Database()
        self.assertTrue( verifyObject(IDatabase, db) )

    def test_2(self):
        "test default values"
        db = Database()
        self.assertEqual( JSONStorage, db._storage_type )
        self.assertEqual( '.', db._root_dir )

    def test_2a(self):
        "test setting values"
        class Foo(object): pass

        table = MyTable()
        db = Database( tables=[table], storage=Foo, root_dir='/foo')
        self.assertTrue( table in db.tables )
        self.assertEqual( Foo, db._storage_type )
        self.assertEqual( '/foo', db._root_dir )

    def test_3(self):
        "test filenames"

        table = MyTable()
        db = Database( tables=[table], storage=JSONStorage, root_dir=curr_dir)

        self.assertEqual( os.path.join(curr_dir,'MyTable.json'), db.get_filename(table) )

    def test_4(self):
        "test overriding filenames"

        table = MyTable(filename='foo.bar')
        db = Database( tables=[table], storage=JSONStorage, root_dir=curr_dir)

        self.assertEqual( os.path.join(curr_dir,'foo.bar'), db.get_filename(table) )
