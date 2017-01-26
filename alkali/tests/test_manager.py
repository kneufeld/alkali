import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt
import json

from alkali.model import Model
from alkali.manager import IManager, Manager
from alkali.storage import JSONStorage
from alkali.query import Query
from alkali import fields
from alkali import tznow

from . import EmptyModel, MyModel

class TestManager( unittest.TestCase ):

    def tearDown(self):
        MyModel.objects.clear()

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IManager, Manager) )

        man = Manager(MyModel)
        self.assertTrue( verifyObject(IManager, man) )
        self.assertEqual( "MyModelManager", man._name )

        self.assertTrue( repr(man) )
        self.assertTrue( str(man) )
        self.assertTrue( unicode(man) )

    def test_2(self):
        "test saving"

        man = Manager(MyModel)

        # no primary key in m1
        m1 = MyModel()
        self.assertRaises( AssertionError, man.save, m1 )

        # successful save
        m1.int_type = 1
        self.assertEqual( 1, m1.int_type )
        self.assertEqual( 1, m1.pk )

        man.save(m1)
        self.assertEqual( 1, len(man) )
        self.assertEqual( 1, man.count )

        # same primary key, same len
        man.save(m1)
        self.assertEqual( 1, len(man) )

    def test_2a(self):
        "changing primary key is not allowed"

        m1 = MyModel()
        m1.int_type = 1

        with self.assertRaises( RuntimeError ):
            m1.int_type = 2

    def test_3(self):
        "test deleting"

        man = Manager(MyModel)

        m1 = MyModel(int_type=1)
        man.save(m1, dirty=False)
        self.assertEqual( 1, len(man) )

        man.delete(m1)
        self.assertEqual( 0, len(man) )

        # make sure deleting a non-existant instance is a no-op
        man.delete(m1)
        self.assertEqual( 0, len(man) )

        self.assertTrue( man.dirty )

    def test_4(self):
        "test getting"

        man = MyModel.objects

        m1 = MyModel(int_type=1)
        man.save(m1)

        m2 = man.get(m1.pk)
        self.assertDictEqual( m1.dict, m2.dict )

        # does not exist
        self.assertRaises( KeyError, man.get, 2 )

        MyModel(int_type=2).save()
        self.assertRaises( KeyError, man.get, int_type__gt=0  )

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
        man.store( storage, force=True ) # just make sure force works
        man.store( storage ) # now verify this is a no op

        from_disk = [e for e in storage.read(MyModel)]
        self.assertDictEqual( d, from_disk[0] )

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

    def test_7(self):
        "test pks"

        man = MyModel.objects

        man.save( MyModel(int_type=1) )
        man.save( MyModel(int_type=2) )
        MyModel(int_type=3).save()
        self.assertEqual( 3, man.count )

        self.assertEqual( [1,2,3], man.pks )

    def test_8(self):
        "test dirty"

        man = MyModel.objects

        m = MyModel(int_type=3).save()
        self.assertFalse( m.dirty )
        self.assertTrue( man.dirty )

        man._dirty = False
        self.assertFalse( man.dirty )

        m.str_type = 'foo'
        self.assertTrue( m.dirty )
        self.assertFalse( man.dirty )

    def test_9(self):
        "verify some simple queries"
        self.assertEqual( Query, type(MyModel.objects.all()) )
        self.assertEqual( Query, type(MyModel.objects.filter()) )

        MyModel(int_type=1).save()
        self.assertEqual( MyModel, type(MyModel.objects.get(1)) )

    def test_10(self):
        "test that bad data throws a pk error"

        tfile = tempfile.NamedTemporaryFile()

        m = MyModel(int_type=1)
        with open(tfile.name,'w') as f:
            f.write( json.dumps([m.dict,m.dict]) )

        man = Manager(MyModel)
        self.assertRaises( KeyError, man.load, JSONStorage(tfile.name) )

    def test_11(self):
        for i in range(10):
            MyModel(int_type=i, str_type='number %d' % i).save()

        self.assertEqual( 0, MyModel.objects.order_by('int_type')[0].int_type )
        self.assertEqual( 9, MyModel.objects.order_by('-int_type')[0].int_type )
