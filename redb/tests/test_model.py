import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.model import IModel, Model
from redb import fields
from redb import tznow

class EmptyModel(Model):
    pass

class MyModel( Model ):
    int_type = fields.IntField(primary_key=True)
    str_type = fields.StringField()
    dt_type  = fields.DateField()

class TestModel( unittest.TestCase ):

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IModel, Model) )

        t = EmptyModel()
        self.assertTrue( verifyObject(IModel, t) )
        self.assertEqual( "EmptyModel", t.name )

    def test_2(self):
        "empty fields by default"
        self.assertEqual( 0, len(EmptyModel().fields) )

    def test_3(self):
        "lets make some fields"
        t = MyModel()
        self.assertEqual( 3, len(t.fields) )

    def test_4(self):
        "set fields in init"
        now = tznow()
        t = MyModel(int_type=3, str_type='string', dt_type=now )
        self.assertEqual( 3, t.int_type )
        self.assertEqual( 'string', t.str_type )
        self.assertEqual( now, t.dt_type )

    def test_4a(self):
        "set fields after init"
        t = MyModel()
        now = tznow()

        t.int_type=3
        t.str_type='string'
        t.dt_type=now

        self.assertEqual( 3, t.int_type )
        self.assertEqual( 'string', t.str_type )
        self.assertEqual( now, t.dt_type )

    def test_5(self):
        "lets make a few instances to make sure there are no overwrites"
        t0 = MyModel()
        self.assertIsNone( t0.int_type )

        t1 = MyModel(int_type=1)
        t2 = MyModel(int_type=2)

        self.assertEqual( 1, t1.int_type )
        self.assertEqual( 2, t2.int_type )

    def test_6(self):
        "test modified flag"

        t = MyModel(int_type=1)
        self.assertFalse( t.modified )

        return # FIXME

        self.assertEqual( int, type(t.int_type) )
        self.assertEqual( fields.IntField, type(t.fields['int_type']) )
        self.assertEqual( 1, t.int_type )
        self.assertTrue( t.modified )

        t.int_type = 2

        self.assertTrue( t.fields['int_type'].modified ) # extraneous
        self.assertTrue( t.modified )
        self.assertEqual( 2, t.int_type )

    def test_7(self):
        "find the primary key"
        t=MyModel()
        self.assertEqual( t.int_type, t.pk )

    def test_8(self):
        "find the filename and str"
        t=MyModel()
        self.assertTrue( t.name in str(t) )
