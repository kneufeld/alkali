import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass

from redb.storage import IStorage, JSONStorage
from . import MyModel

class TestStorage( unittest.TestCase ):

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IStorage, JSONStorage) )

        for storage in [JSONStorage]:
            self.assertTrue( verifyClass(IStorage, storage) )
            s = storage('')
            self.assertTrue( verifyObject(IStorage, s) )

    def test_2(self):
        "write should handle empty dicts vs None"
        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )

        self.assertTrue( storage.write( iter([]) ) )

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
