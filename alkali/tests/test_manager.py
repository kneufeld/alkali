import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt
import json

from alkali.model import Model
from alkali.manager import Manager
from alkali.storage import JSONStorage
from alkali.query import Query
from alkali import fields
from alkali import tznow

from . import MyModel, MyDepModel, Entry

import logging
logger = logging.getLogger('alkali.manager')

class TestManager( unittest.TestCase ):

    def setUp(self):
        self.log_level = logger.getEffectiveLevel()
        logger.setLevel(logging.CRITICAL+1)

    def tearDown(self):
        logger.setLevel(self.log_level)

        MyModel.objects.clear()
        MyDepModel.objects.clear()

    def test_1(self):
        "verify class/instance implementation"

        man = Manager(MyModel)
        self.assertEqual( "MyModelManager", man._name )

        self.assertTrue( repr(man) )
        self.assertTrue( str(man) )

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
        self.assertRaises( KeyError, man.get, 200 )

        MyModel(int_type=2).save()
        self.assertRaises( MyModel.DoesNotExist, man.get, int_type=200  )    # < 1
        self.assertRaises( MyModel.ObjectDoesNotExist, man.get, int_type=200  )    # < 1
        self.assertRaises( MyModel.MultipleObjectsReturned, man.get, int_type__gt=0  )  # > 1

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

        m.save()
        self.assertFalse( m.dirty )
        self.assertTrue( man.dirty )

    def test_9(self):
        "verify some simple queries"
        self.assertEqual( Query, type(MyModel.objects.all()) )
        self.assertEqual( Query, type(MyModel.objects.filter()) )

        MyModel(int_type=1).save()
        self.assertEqual( MyModel, type(MyModel.objects.get(1)) )

    def test_10(self):
        "test that duplicate pk throws an error"

        tfile = tempfile.NamedTemporaryFile()

        m = MyModel(int_type=1)
        with open(tfile.name,'w') as f:
            f.write( json.dumps([m.dict,m.dict]) )

        man = Manager(MyModel)
        self.assertRaises( KeyError, man.load, JSONStorage(tfile.name) )

    def test_10a(self):
        "test that empty pk throws an error"

        tfile = tempfile.NamedTemporaryFile()

        m = MyModel(str_type='string data')
        with open(tfile.name,'w') as f:
            f.write( json.dumps([m.dict,m.dict]) )

        man = Manager(MyModel)
        self.assertRaises( MyModel.EmptyPrimaryKey, man.load, JSONStorage(tfile.name) )

    def test_10b(self):
        "test that loading can continue if foreign model instance is missing"
        tfile = tempfile.NamedTemporaryFile()

        f = MyModel(int_type=1).save()
        m = f.mydepmodel_set.create(pk1=1)

        with open(tfile.name,'w') as f:
            f.write( json.dumps([m.dict]) )

        MyModel.objects.clear()

        man = Manager(MyDepModel)
        self.assertIsNone( man.load(JSONStorage(tfile.name)) )

        self.assertEqual( 0, man.count )

    def test_11(self):
        for i in range(10):
            MyModel(int_type=i, str_type='number %d' % i).save()

        self.assertEqual( 0, MyModel.objects.order_by('int_type')[0].int_type )
        self.assertEqual( 9, MyModel.objects.order_by('-int_type')[0].int_type )

    def test_14(self):
        "test that Manager.instances return a list not its dict"
        self.assertTrue( isinstance(MyModel.objects.instances, list) )

    def test_15(self):
        "test that Manager.instances returns a copy of object"
        m = MyModel(int_type=1).save()

        # make sure ingoing model gets copied
        self.assertNotEqual( id(m), id(MyModel.objects._instances[m.pk]) )

        m1 = MyModel.objects.get(m.pk)
        m2 = MyModel.objects.get(m.pk)
        self.assertNotEqual( id(m1), id(m2) )

    def test_no_storage(self):
        MyModel.objects.store(None)
        MyModel.objects.load(None)

    def test_create_with_pk_kwarg(self):
        # creating an instance with 'pk' keyword didn't originally work as expected
        now = dt.datetime.now()
        e = Entry(pk=now).save()

        self.assertTrue(Entry.objects.get(now))

        # don't pass in 'pk' and actual pk field name
        with self.assertRaises(AssertionError):
            Entry(pk=now, date=now)

    def test_get_or_create(self):
        m1 = MyModel.objects.get_or_create(int_type=1)
        self.assertEqual(1, m1.int_type)
        self.assertEqual(1, MyModel.objects.get(int_type=1).int_type)

        m2 = MyModel.objects.get_or_create(int_type=1)
        self.assertEqual(1, m2.int_type)
        self.assertEqual(1, MyModel.objects.get(int_type=1).int_type)

        self.assertEqual(1, MyModel.objects.count)
