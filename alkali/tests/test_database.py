import os
import unittest
import tempfile
import inspect

from alkali.database import Database
from alkali.model import Model
from alkali.storage import JSONStorage, Storage, MultiStorage
from alkali import fields
from alkali import tznow

from . import MyModel, AutoModel1, AutoModel2

curr_dir = os.path.dirname( os.path.abspath( __file__ ) )

class FooStorage(Storage):
    extension = 'foo'

class TestDatabase( unittest.TestCase ):

    def tearDown(self):
        # cleanup any created data files
        from os import getcwd
        from os.path import join

        for d in [getcwd(), join(getcwd(), 'alkali', 'tests')]:
            for f in ['MyModel.json', 'foo.bar']:
                t = join(d, f)
                if os.path.isfile(t):
                    os.unlink(t)

        AutoModel1.objects.clear()
        AutoModel2.objects.clear()

    def test_1(self):
        "verify instantiation"
        self.assertTrue( Database() )
        self.assertTrue( FooStorage(None) )

    def test_2(self):
        "test default values"
        db = Database()
        self.assertEqual( JSONStorage, db._storage_type )
        self.assertEqual( os.getcwd(), db._root_dir )
        self.assertEqual( False, db._save_on_exit )

    def test_2a(self):
        "test setting values"

        model = MyModel
        db = Database( models=[model], storage=FooStorage, root_dir='/foo')
        self.assertTrue( model in db.models )
        self.assertEqual( FooStorage, db._storage_type )
        self.assertEqual( '/foo', db._root_dir )

    def test_3(self):
        "test filenames"

        db = Database( models=[MyModel], storage=JSONStorage, root_dir=curr_dir)
        self.assertEqual( os.path.join(curr_dir,'MyModel.json'), db.get_filename(MyModel) )

    def test_4(self):
        "test overriding filenames"

        class MyModel( Model ):

            class Meta:
                filename = 'foo.bar'

            int_type = fields.IntField(primary_key=True)
            str_type = fields.StringField()
            date_type  = fields.DateTimeField()

        model = MyModel
        db = Database( models=[model], storage=JSONStorage, root_dir=curr_dir)

        self.assertEqual( db.get_filename(model), db.get_filename('MyModel') )
        self.assertEqual( os.path.join(curr_dir,'foo.bar'), db.get_filename(model) )

        # make sure we don't prepend curr_dir if we give full path
        MyModel.Meta.filename = '/path/foo.bar'
        self.assertEqual( os.path.join('/path','foo.bar'), db.get_filename(model) )

    def test_5(self):
        "test overriding storage"

        class MyModel( Model ):
            class Meta:
                storage = FooStorage

            int_type = fields.IntField(primary_key=True)
            str_type = fields.StringField()
            date_type  = fields.DateTimeField()

        model = MyModel
        db = Database( models=[model], storage=JSONStorage, root_dir=curr_dir)

        self.assertEqual( db.get_storage(model), db.get_storage('MyModel') )
        self.assertEqual( FooStorage, db.get_storage(model).__class__ )

        self.assertTrue( inspect.isclass(FooStorage) )
        self.assertTrue( db.get_storage(model) )

        db.set_storage(MyModel, FooStorage)
        self.assertEqual( FooStorage, db.get_storage(model).__class__ )

        db.set_storage('MyModel', FooStorage)
        self.assertEqual( FooStorage, db.get_storage(model).__class__ )

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
            dt_type  = fields.DateTimeField()

        db = Database( models=[MyModel] )
        man = MyModel.objects

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]

        for inst in instances:
            man.save(inst)

        db.store()
        self.assertTrue( os.path.getsize(tfile.name) )
        del db

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
            dt_type  = fields.DateTimeField()

        # make sure we're starting with an empty file
        self.assertFalse( open( tfile.name, 'r').read() )

        db = Database( models=[MyModel], save_on_exit=True )

        now = tznow()
        m = MyModel(int_type=1, str_type='string', dt_type=now )
        m.save()
        self.assertEqual( 1, len(MyModel.objects) )

        del db # save_on_exit is true

        self.assertTrue( open( tfile.name, 'r').read() )

    def test_no_primary_key(self):
        tfile = tempfile.NamedTemporaryFile()

        class MyModel2( Model ):
            class Meta:
                filename = tfile.name

            int_type = fields.IntField(primary_key=True)

        db = Database( models=[MyModel2] )

        for i in range(3):
            MyModel2(int_type=i).save()

        db.store()
        self.assertTrue( os.path.getsize(tfile.name) )
        del db

        # need to add a auto increment for when there is no pk
        # and/or assert when model doesn't have pk
        # all records read/write to None/'' when there is no pk
        #print "fread",open(tfile.name,'r').read()

        db = Database( models=[MyModel2] )
        db.load()

        # not sure if this is a valid test, MyModel.objects is still around
        model = db.get_model('MyModel2')
        self.assertEqual( 3, len(model.objects) )

    def test_two_models(self):

        class MyModel2(Model):
            class Meta:
                storage = FooStorage

            pk1     = fields.IntField(primary_key=True)

        # MyModel.Meta.storage = JSONStorage
        # MyModel2.Meta.storage = FooStorage

        db = Database(models=[MyModel, MyModel2])

        self.assertEqual( JSONStorage, db.get_storage(MyModel).__class__ )
        self.assertEqual( FooStorage, db.get_storage(MyModel2).__class__ )

    def test_bad_load(self):
        db = Database(models=[MyModel])
        self.assertIsNone( db.get_storage(self.__class__) )

    def test_storage_instance(self):
        tfile = tempfile.NamedTemporaryFile(mode="w")

        db = Database(
            models=[AutoModel1, AutoModel2],
            storage=MultiStorage([AutoModel1, AutoModel2], tfile.name)
        )
        db.load()

        AutoModel1(f1="some text 1").save()
        AutoModel2(f1="some text 1").save()

        db.store()
        db = None

        AutoModel1.objects.clear()
        AutoModel2.objects.clear()

        db = Database(
            models=[AutoModel1, AutoModel2],
            storage=MultiStorage([AutoModel1, AutoModel2], tfile.name)
        )
        db.load()

        self.assertEqual("some text 1", AutoModel1.objects.get(f1="some text 1").f1)
        self.assertEqual("some text 1", AutoModel2.objects.get(f1="some text 1").f1)
