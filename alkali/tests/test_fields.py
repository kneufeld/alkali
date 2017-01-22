# encoding: utf-8

import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from alkali.fields import IField, Field, IntField, StringField
from alkali.fields import DateTimeField, FloatField, SetField
from alkali.fields import ForeignKey
from alkali import tznow, tzadd
from alkali.model import Model

from alkali.tests import MyModel, MyMulti, MyDepModel


class TestField( unittest.TestCase ):

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IField, Field) )

        for field in [IntField, StringField, DateTimeField, FloatField, SetField]:
            self.assertTrue( verifyClass(IField, field) )
            f = field()
            self.assertTrue( verifyObject(IField, f) )
            self.assertTrue( str(f) )

    def test_2(self):
        "Field is a meta class, it has no value. make sure of that"
        f = IntField()
        with self.assertRaises(AttributeError):
            f.value
        with self.assertRaises(AttributeError):
            f._value

    def test_4(self):
        "test primary key setting"
        f = IntField()
        self.assertEqual( False, f.primary_key )

        f = IntField( primary_key=True )
        self.assertEqual( True, f.primary_key )

    def test_5(self):
        "test date setting"
        now = dt.datetime.now()
        f = DateTimeField()
        v = f.cast(now)

        self.assertIsNotNone( v.tzinfo )

        v = f.cast(v) # keeps tzinfo
        self.assertIsNotNone( v.tzinfo )

        v = f.cast('now')
        self.assertEqual( dt.datetime, type(v) )

        v = f.loads('2016-07-20 17:53')
        self.assertEqual( dt.datetime, type(v) )

        self.assertRaises( TypeError, f.cast, 1 )

    def test_6(self):
        "test SetField"
        s=set([1,2,3])
        f = SetField()

        v = f.cast(s)
        self.assertEqual( s, v )

        self.assertEqual( s, f.loads( f.dumps(s) ) )

    def test_7(self):
        "test StringField"
        s = "ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ"

        f = StringField()

        v = f.cast(s)
        self.assertEqual( s.decode('utf-8'), v )
        self.assertEqual( v, f.loads( f.dumps(v) ) )

    def test_8(self):
        "test none/null"
        f = DateTimeField()

        v = f.loads(None)
        self.assertIsNone(v)

        v = f.loads('null')
        self.assertIsNone(v)

    def test_10(self):
        "test foreign keys, link to multi pk model"
        with self.assertRaises(AssertionError):
            class MyDepModelMulti(Model):
                pk      = IntField(primary_key=True)
                foreign = ForeignKey(MyMulti)

    def test_11(self):
        """
        test foreign keys
        note: just being able to define MyDepModel runs lots of code
        """
        m = MyModel(int_type=1).save()
        d = MyDepModel(pk=1, foreign=m)
        self.assertEqual( id(m), id(d.foreign) )

        d = MyDepModel(pk=1, foreign=1) # foreign key value
        self.assertEqual( id(m), id(d.foreign) )

        d.foreign.str_type = "hello world"
        self.assertEqual( "hello world", m.str_type )
