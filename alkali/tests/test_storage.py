import os
import unittest
import tempfile
import csv
from zope.interface.verify import verifyObject, verifyClass

from alkali.storage import IStorage, FileStorage, JSONStorage, CSVStorage
from alkali import tznow
from . import MyModel, MyDepModel

class TestStorage( unittest.TestCase ):

    def tearDown(self):
        MyModel.objects.clear()
        MyDepModel.objects.clear()

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IStorage, JSONStorage) )

        for storage in [FileStorage,JSONStorage]:
            self.assertTrue( verifyClass(IStorage, storage) )
            self.assertTrue( verifyObject(IStorage, storage('') ) )

    def test_2(self):
        "write should handle empty dicts vs None"
        tfile = tempfile.NamedTemporaryFile()

        for storage in [FileStorage,JSONStorage]:
            self.assertTrue( storage(tfile.name).write( iter([]) ) )
            self.assertFalse( storage(tfile.name).write( None ) )

    def test_3(self):
        "test simple reading and writing"

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )

        entries = [MyModel(int_type=1), MyModel(int_type=2)]
        self.assertTrue( storage.write(entries) )

        size = os.path.getsize(tfile.name)
        self.assertTrue( size > 0 )

        loaded = [e for e in storage.read(MyModel)]
        self.assertEqual( 2, len(loaded) )

        for a,b in zip(entries,loaded):
            self.assertDictEqual( a.dict, b )

    def test_3a(self):
        "test writing no data"

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )

        self.assertTrue( storage.write([]) )

        # with open(tfile.name) as f:
            # print f.read()

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
        tfile = tempfile.NamedTemporaryFile()
        storage = FileStorage( tfile.name )

        models = [ MyModel() ]

        # TODO test that we can recover original object data
        self.assertTrue( storage.write( models ) )
        self.assertTrue( open( tfile.name, 'r').read() )
        self.assertTrue( storage.read(MyModel) )

    def test_10(self):
        "test saving foreign key"
        m = MyModel(int_type=1).save()
        d = MyDepModel(pk1=10, foreign=m).save()

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )
        storage.write([m])

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )
        storage.write([d])

    def test_15(self):
        "test CSVStorage"

        tfile = tempfile.NamedTemporaryFile()

        self.assertFalse( CSVStorage( tfile.name ).write(None) )

        now = tznow()
        m1 = MyModel(int_type=1, str_type='a string, with comma', dt_type=now).save()
        m2 = MyModel(int_type=2, str_type='a string, with comma', dt_type=now).save()

        storage = CSVStorage( tfile.name )
        storage.write([m1,m2])

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

            for k in row.keys():
                results_key = k.lower().replace(' ', '_')

                if results_key not in fields:
                    if k == 'Bad Name':
                        results_key = 'dt_type'
                    else:
                        raise RuntimeError( "unknown field: {}".format(k) ) # pragma: nocover

                row[results_key] = row.pop(k)

            return row

        tfile = tempfile.NamedTemporaryFile()

        now = tznow()
        m = MyModel(int_type=1, str_type='a string, with comma', dt_type=now).save()

        with open( tfile.name, 'w' ) as f:
            d = { 'Int Type':1,
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
