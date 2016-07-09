import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass

from redb.storage import IStorage, JSONStorage

class TestStorage( unittest.TestCase ):

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IStorage, JSONStorage) )

        storage = JSONStorage('')
        self.assertTrue( verifyObject(IStorage, storage) )

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

    def test_5(self):
        "make sure our filename ends with extension"

        tfile = tempfile.NamedTemporaryFile()
        storage = JSONStorage( tfile.name )
        #self.assertTrue( storage.filename.endswith( storage.extension ) )
