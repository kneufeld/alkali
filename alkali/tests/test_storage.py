import os
import unittest
import tempfile
import csv
import json

from alkali import Model, fields
from alkali.storage import FileStorage, JSONStorage, CSVStorage, MultiStorage
from alkali.storage import FileAlreadyLocked, Storage
from alkali import tznow
from . import MyModel, MyDepModel, AutoModel1, AutoModel2


class TestStorage( unittest.TestCase ):

    def tearDown(self):
        MyModel.objects.clear()
        MyDepModel.objects.clear()
        AutoModel1.objects.clear()
        AutoModel2.objects.clear()

    def test_1(self):
        "verify class/instance implementation"
        # self.assertTrue( verifyClass(IStorage, JSONStorage) )

        # from zope.interface.verify import verifyObject, verifyClass
        # for storage in [FileStorage, JSONStorage]:
        #     self.assertTrue( verifyClass(IStorage, storage) )
        #     self.assertTrue( verifyObject(IStorage, storage(None) ) )

    def test_notimplemented(self):
        with self.assertRaises(NotImplementedError):
            Storage().read(None)

        with self.assertRaises(NotImplementedError):
            Storage().write(None, None)

    def test_2(self):
        "write should handle empty dicts vs None"
        tfile = tempfile.NamedTemporaryFile()

        for storage in [FileStorage, JSONStorage, CSVStorage]:
            self.assertTrue( storage(tfile.name).write(MyModel, iter([])) )
            self.assertFalse( storage(tfile.name).write(MyModel, None) )

        for storage in [MultiStorage]:
            self.assertTrue( storage([MyModel], tfile.name).write(MyModel, iter([])) )
            self.assertFalse( storage([MyModel], tfile.name).write(MyModel, None) )

    def test_3(self):
        "test simple reading and writing"

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )

        entries = [MyModel(int_type=1), MyModel(int_type=2)]
        self.assertTrue( storage.write(MyModel, entries) )

        size = os.path.getsize(tfile.name)
        self.assertTrue( size > 0 )

        loaded = [e for e in storage.read(MyModel)]
        self.assertEqual( 2, len(loaded) )

        for a, b in zip(entries, loaded):
            self.assertDictEqual( a.dict, b )

    def test_3a(self):
        "test writing no data"

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )

        self.assertTrue( storage.write(MyModel, []) )

        # with open(tfile.name) as f:
        #     print f.read()

        size = os.path.getsize(tfile.name)
        self.assertEqual( 4, size )

        loaded = [e for e in storage.read(MyModel)]
        self.assertEqual( 0, len(loaded) )

    def test_3b(self):
        "test reading empty file"
        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )

        loaded = [e for e in storage.read(MyModel)]
        self.assertEqual( 0, len(loaded) )

    def test_4(self):
        "make sure we're setting extension"
        self.assertEqual( 'json', JSONStorage.extension )

    def test_5(self):
        "test plain FileStorage class"
        # FIXME this is a crap test, it just read/writes a string
        tfile = tempfile.NamedTemporaryFile()
        storage = FileStorage( tfile.name )

        m1 = MyModel(int_type=1, str_type="str", dt_type=tznow())

        self.assertTrue( storage.write(MyModel, [m1]) )
        self.assertTrue( open( tfile.name, 'r').read() )

        m2 = storage.read(MyModel)
        self.assertTrue(m2)
        self.assertEqual(str(m1), m2)

    def test_10(self):
        "test saving foreign key"
        m = MyModel(int_type=1).save()
        d = MyDepModel(pk1=10, foreign=m).save()

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )
        storage.write(MyModel, [m])

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )
        storage.write(MyDepModel, [d])

    def test_15(self):
        "test CSVStorage"

        tfile = tempfile.NamedTemporaryFile()

        self.assertFalse( CSVStorage( tfile.name ).write(MyModel, None) )

        now = tznow()
        m1 = MyModel(int_type=1, str_type='a string, with comma', dt_type=now).save()
        m2 = MyModel(int_type=2, str_type='a string, with comma', dt_type=now).save()

        storage = CSVStorage( tfile.name )
        storage.write(MyModel, [m1, m2])
        del storage

        # with open(tfile.name, 'r') as f:
        #     print f.read()

        storage = CSVStorage( tfile.name )

        loaded = [e for e in storage.read(MyModel)]
        self.assertEqual(2, len(loaded))

        m = loaded[0]

        self.assertEqual(1, m.int_type)
        self.assertEqual('a string, with comma', m.str_type)
        self.assertEqual(now, m.dt_type)

    def test_16(self):
        "test CSVStorage with wrong header"
        def remap_fieldnames(model_class, row):
            fields = model_class.Meta.fields.keys()

            for k in list(row.keys()):
                results_key = k.lower().replace(' ', '_')

                if results_key not in fields:
                    if k == 'Bad Name':
                        results_key = 'dt_type'

                row[results_key] = row.pop(k)

            return row

        tfile = tempfile.NamedTemporaryFile()

        now = tznow()
        m = MyModel(int_type=1, str_type='a string, with comma', dt_type=now).save()

        with open( tfile.name, 'w' ) as f:
            d = { 'Int Type': 1,
                    'Str Type': 'a string, with comma',
                    'Bad Name': now}
            writer = csv.DictWriter(f, fieldnames=d.keys())
            writer.writeheader()
            writer.writerow(d)

        # with open(tfile.name, 'r') as f:
        #     print f.read()

        m = MyModel(int_type=1, str_type='a string, with comma', dt_type=now).save()

        storage = CSVStorage( tfile.name )
        storage.remap_fieldnames = remap_fieldnames

        loaded = [e for e in storage.read(MyModel)]
        self.assertEqual(1, len(loaded))

        m = loaded[0]

        self.assertEqual(1, m.int_type)
        self.assertEqual('a string, with comma', m.str_type)
        self.assertEqual(now, m.dt_type)

    def test_locking(self):
        if os.name == 'nt': # pragma: nocover
            return # windows doesn't have fcntl

        tfile = tempfile.NamedTemporaryFile()
        stor1 = FileStorage( tfile.name )

        with self.assertRaises(FileAlreadyLocked):
            FileStorage( tfile.name )

        del stor1 # release lock
        FileStorage( tfile.name ) # shouldn't raise

    def test_changing_filename(self):
        tfile1 = tempfile.NamedTemporaryFile()
        tfile2 = tempfile.NamedTemporaryFile()

        stor1 = FileStorage( tfile1.name )
        self.assertEqual( stor1.filename, tfile1.name )

        stor1.filename = tfile2.name
        self.assertEqual( stor1.filename, tfile2.name )

        stor1.filename = None
        self.assertEqual( stor1.filename, None )

    def test_creating_new_file(self):
        tname = tempfile.NamedTemporaryFile().name
        FileStorage( tname )

        self.assertTrue( os.path.isfile(tname) )

    def test_pass_file_handle(self):
        tfile = tempfile.NamedTemporaryFile()
        stor1 = FileStorage( tfile )

        self.assertEqual( tfile.name, stor1.filename )

    def test_safe_lock(self):
        FileStorage( None ).lock()

    def test_multi_flock(self):
        if os.name == 'nt': # pragma: nocover
            return # windows doesn't have fcntl

        tfile = tempfile.NamedTemporaryFile(mode="w")

        with self.assertRaises(FileAlreadyLocked):
            (
                MultiStorage([AutoModel1, AutoModel2], tfile.name),
                MultiStorage([AutoModel1, AutoModel2], tfile.name)
            )

    def test_multi_1(self):
        tfile = tempfile.NamedTemporaryFile(mode="w")

        storage = MultiStorage([AutoModel1, AutoModel2], tfile.name)

        AutoModel1(f1="some text 1").save()
        AutoModel1(f1="some text 2").save()

        m1 = AutoModel1.objects.get(f1__contains='2')

        AutoModel1.objects.store(storage)
        AutoModel2.objects.store(storage) # empty list
        assert os.path.getsize(tfile.name)

        AutoModel1.objects.load(storage)

        m2 = AutoModel1.objects.get(f1__contains='2')
        self.assertEqual(m1, m2)

        # db = Database(models=[AutoModel1, AutoModel2], storage=storage, save_on_exit=False)

    def test_multi_2(self):
        tfile = tempfile.NamedTemporaryFile(mode="w")

        storage = MultiStorage([AutoModel1, AutoModel2], tfile.name)

        AutoModel1(f1="some text 1").save()
        AutoModel1(f1="some text 2").save()

        AutoModel2(f1="some text 1").save()
        AutoModel2(f1="some text 2").save()
        AutoModel2(f1="some text 3").save()

        AutoModel1.objects.store(storage)
        AutoModel2.objects.store(storage)

        # with open(tfile.name, 'r') as f:
        #     print("\nSTART\n")
        #     print(f.read())
        #     print("\nEND\n")

        with open(tfile.name, 'r') as f:
            data = json.load(f)

        self.assertEqual(2, len(data.keys()))
        self.assertEqual(2, len(data['automodel1']))
        self.assertEqual(3, len(data['automodel2']))
