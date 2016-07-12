import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.model import Model
from redb.manager import IManager, Manager
from redb.storage import JSONStorage
from redb import fields
from redb import tznow

from . import EmptyModel, MyModel

class TestManager( unittest.TestCase ):

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IManager, Manager) )

        man = Manager(MyModel)
        self.assertTrue( verifyObject(IManager, man) )
        self.assertEqual( "MyModelManager", man.name )

    def test_2(self):
        "test saving"

        man = Manager(MyModel)

        # no primary key in m1
        m1 = MyModel()
        self.assertRaises( AssertionError, man.save, m1 )

        # successful save
        m1.int_type = 1
        man.save(m1)
        self.assertEqual( 1, len(man) )

        # same primary key, same len
        man.save(m1)
        self.assertEqual( 1, len(man) )

        # different primary key, new len
        m1.int_type = 2
        man.save(m1)
        self.assertEqual( 2, len(man) )

    def test_3(self):
        "test deleting"

        man = Manager(MyModel)

        m1 = MyModel(int_type=1)
        man.save(m1)
        self.assertEqual( 1, len(man) )

        man.delete(m1)
        self.assertEqual( 0, len(man) )

        # make sure deleting a non-existant instance is a no-op
        man.delete(m1)
        self.assertEqual( 0, len(man) )

    def test_4(self):
        "test getting"

        man = Manager(MyModel)

        m1 = MyModel(int_type=1)
        man.save(m1)

        m2 = man.get(m1.pk)
        self.assertDictEqual( m1.dict, m2.dict )

        # does not exist
        self.assertRaises( KeyError, man.get, 2 )

    def test_5(self):
        "test saving actual model objects"

        tfile = tempfile.NamedTemporaryFile()

        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now )
        d={u'int_type':3, u'str_type':u'string', u'dt_type':now.isoformat()}

        man = Manager(MyModel)
        man.save(m)

        storage = JSONStorage(tfile.name)
        man.store( storage )

        from_disk = [e for e in storage.read(MyModel)]
        self.assertDictEqual( d, from_disk[0].dict )

    def test_6(self):
        "test loading actual model objects"

        tfile = tempfile.NamedTemporaryFile()

        now = tznow()
        m1 = MyModel(int_type=3, str_type='string', dt_type=now )

        man = Manager(MyModel)
        man.save(m1)

        storage = JSONStorage(tfile.name)
        man.store( storage )

        man = Manager(MyModel)
        self.assertRaises( KeyError, man.get, m1.pk )

        man.load( storage )
        m2 = man.get(m1.pk)

        self.assertDictEqual( m1.dict, m2.dict )
