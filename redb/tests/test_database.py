import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.database import IDatabase, Database
from redb.model import IModel, Model
from redb.storage import JSONStorage, TextStorage
from redb import fields
from . import MyModel

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

        model = MyModel()
        db = Database( models=[model], storage=Foo, root_dir='/foo')
        self.assertTrue( model in db.models )
        self.assertEqual( Foo, db._storage_type )
        self.assertEqual( '/foo', db._root_dir )

    def test_3(self):
        "test filenames"

        model = MyModel()
        db = Database( models=[model], storage=JSONStorage, root_dir=curr_dir)

        self.assertEqual( os.path.join(curr_dir,'MyModel.json'), db.get_filename(model) )

    def test_4(self):
        "test overriding filenames"

        class MyModel( Model ):

            class Meta:
                filename = 'foo.bar'

            int_type = fields.IntField()
            str_type = fields.StringField()
            date_type  = fields.DateField()

        model = MyModel()
        db = Database( models=[model], storage=JSONStorage, root_dir=curr_dir)

        self.assertEqual( os.path.join(curr_dir,'foo.bar'), db.get_filename(model) )

    def test_5(self):
        "test overriding storage"

        class MyModel( Model ):

            class Meta:
                storage = TextStorage

            int_type = fields.IntField()
            str_type = fields.StringField()
            date_type  = fields.DateField()

        model = MyModel()
        db = Database( models=[model], storage=JSONStorage, root_dir=curr_dir)

        self.assertEqual( TextStorage, db.get_storage(model) )
