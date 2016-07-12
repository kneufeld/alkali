import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.model import Model
from redb.query import IQuery, Query
from redb.storage import JSONStorage
from redb import fields
from redb import tznow

from . import EmptyModel, MyModel

class TestQuery( unittest.TestCase ):

    def tearDown(self):
        MyModel.objects.clear()

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IQuery, Query) )

        q = Query(MyModel.objects)
        self.assertTrue( verifyObject(IQuery, q) )


    def test_2(self):
        "make sure Manager is returning a query object"
        man = MyModel.objects
        self.assertEqual( Query, type(man.filter()) )

    def test_3(self):
        "make sure field helpers work"
        q = Query(MyModel.objects)
        self.assertTrue( 'int_type' in q.field_names )
        self.assertTrue( 'str_type' in q.field_names )
        self.assertTrue( 'dt_type' in q.field_names )

    def test_5(self):
        "make sure query doesn't change after manager does"

        man = MyModel.objects
        q = Query(man)
        self.assertEqual( 0, len(q) )

        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now )
        m.save()

        self.assertEqual( 0, len(q) )
        self.assertEqual( 1, len(man) )

    def test_10(self):
        "make sure query gets instances"

        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now )
        m.save()

        man = MyModel.objects
        q = Query(man)

        self.assertEqual( 1, len(q) )
        self.assertEqual( 1, len(man) )

    def test_15(self):
        "make sure query objects are 'updated' when manager objects changes"

        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now )
        m.save()

        man = MyModel.objects
        q = Query(man)

        mq = q.instances[0]
        self.assertEqual( m.str_type, mq.str_type )

        m.str_type = 'new string'
        self.assertEqual( m.str_type, mq.str_type )

    def test_20(self):
        "test filter function"
        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        for i in range(3):
            q = MyModel.objects.filter(int_type=i)
            self.assertEqual( 1, len(q) )
            self.assertEqual( i, q.instances[0].int_type )

    def test_21(self):
        "test different filter functions"

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        results = MyModel.objects.filter(int_type__eq=0).instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(int_type__gt=0).instances
        self.assertEqual( 2, len(results) )

        results = MyModel.objects.filter(int_type=0, str_type='string').instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(int_type=0, str_type='string XXX').instances
        self.assertEqual( 0, len(results) )

        # test pk queries
        results = MyModel.objects.filter(pk=1).instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.get(pk=1)
        self.assertEqual( MyModel, type(results) )

    def test_25(self):
        "test chaining filters together"

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        q = MyModel.objects.filter(int_type__gt=0).filter(int_type=1)
        self.assertEqual( 1, len(q) )

    def test_30(self):
        "test query iteration"

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        q = MyModel.objects.filter()
        c = 0
        for i in q:
            c += 1

        self.assertEqual( 3, c )