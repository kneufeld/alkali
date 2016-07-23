import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.database import IDatabase, Database
from redb.model import IModel, Model
from redb.storage import JSONStorage, Storage
from redb import fields
from redb import tznow
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

        class FooStorage(Storage):
            pass

        class MyModel( Model ):

            class Meta:
                storage = FooStorage

            int_type = fields.IntField()
            str_type = fields.StringField()
            date_type  = fields.DateField()

        model = MyModel()
        db = Database( models=[model], storage=JSONStorage, root_dir=curr_dir)

        self.assertEqual( FooStorage, db.get_storage(model) )

    def test_get_models(self):
        db = Database( models=[MyModel] )
        self.assertTrue( db.get_model('MyModel') )
        self.assertIsNone( db.get_model('NotAModel') )

    def test_6(self):
        "test saving/loading"

        tfile = tempfile.NamedTemporaryFile()

        class MyModel( Model ):
            class Meta:
                ordering = ['int_type','str_type','dt_type']
                filename = tfile.name

            int_type = fields.IntField(primary_key=True)
            str_type = fields.StringField()
            dt_type  = fields.DateField()

        db = Database( models=[MyModel] )
        man = MyModel.objects

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]

        for inst in instances:
            man.save(inst)

        db.store()
        self.assertTrue( os.path.getsize(tfile.name) )

        # with open(tfile.name,'r') as f:
        #     print f.read()

        db = Database( models=[MyModel] )
        db.load()

        # not sure if this is a valid test, MyModel.objects is still around
        model = db.get_model('MyModel')
        self.assertEqual( 3, len(model.objects) )

    def test_save_on_exit(self):
        "make sure we can actually save a database"

        tfile = tempfile.NamedTemporaryFile()

        class MyModel( Model ):
            class Meta:
                ordering = ['int_type','str_type','dt_type']
                filename = tfile.name

            int_type = fields.IntField(primary_key=True)
            str_type = fields.StringField()
            dt_type  = fields.DateField()

        with open( tfile.name, 'r') as f:
            data = f.read()
        self.assertFalse( data )

        db = Database( models=[MyModel], save_on_exit=True )

        now = tznow()
        m = MyModel(int_type=1, str_type='string', dt_type=now )
        m.save()
        self.assertEqual( 1, len(MyModel.objects) )

        del db

        with open( tfile.name, 'r') as f:
            data = f.read()
        self.assertTrue( data )
