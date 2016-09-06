import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass

from alkali.storage import IStorage, Storage, FileStorage, JSONStorage
from . import MyModel

class TestStorage( unittest.TestCase ):

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
