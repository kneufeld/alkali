import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass

from redb.storage import IStorage, JSONStorage, TextStorage

class TestStorage( unittest.TestCase ):

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IStorage, JSONStorage) )

        for storage in [JSONStorage, TextStorage]:
            self.assertTrue( verifyClass(IStorage, storage) )
            s = storage('')
            self.assertTrue( verifyObject(IStorage, s) )

    def test_2(self):
        "write should handle empty dicts vs None"
        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )

        self.assertFalse( storage.write( None ) )
        self.assertTrue( storage.write( {} ) )

    def test_3(self):
        "test simple reading and writing"

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )

        d = { u'key1': u'a string', '2': 4 }

        self.assertTrue( storage.write(d) )

        size = os.path.getsize(tfile.name)
        self.assertTrue( size > 0 )

        data = storage.read()
        self.assertDictEqual( d, data )

    def test_4(self):
        "make sure we're setting extension"
        self.assertEqual( 'json', JSONStorage.extension )
