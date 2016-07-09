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

        m = EmptyModel()
        self.assertTrue( verifyObject(IModel, m) )
        self.assertEqual( "EmptyModel", m.name )

        self.assertTrue( m.schema ) # make sure it doesn't blow up

    def test_2(self):
        "empty fields by default"
        self.assertEqual( 0, len(EmptyModel().fields) )

    def test_3(self):
        "lets make some fields"
        m = MyModel()
        self.assertEqual( 3, len(m.fields) )

    def test_4(self):
        "set fields in init"
        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now )
        self.assertEqual( 3, m.int_type )
        self.assertEqual( 'string', m.str_type )
        self.assertEqual( now, m.dt_type )

    def test_4a(self):
        "set fields after init"
        m = MyModel()
        now = tznow()

        m.int_type=3
        m.str_type='string'
        m.dt_type=now

        self.assertEqual( 3, m.int_type )
        self.assertEqual( 'string', m.str_type )
        self.assertEqual( now, m.dt_type )

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

        m = MyModel(int_type=1)
        self.assertFalse( m.modified )

        return # FIXME

        self.assertEqual( int, type(m.int_type) )
        self.assertEqual( fields.IntField, type(m.fields['int_type']) )
        self.assertEqual( 1, m.int_type )
        self.assertTrue( m.modified )

        m.int_type = 2

        self.assertTrue( m.fields['int_type'].modified ) # extraneous
        self.assertTrue( m.modified )
        self.assertEqual( 2, m.int_type )

    def test_7(self):
        "find the primary key"
        m=MyModel()
        self.assertEqual( m.int_type, m.pk )

    def test_8(self):
        "find the filename and str"
        m=MyModel()
        self.assertTrue( m.name in str(m) )

    def test_9(self):
        "test dict"

        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now )

        d={'int_type':3, 'str_type':'string', 'dt_type':now.isoformat()}
        self.assertDictEqual( d, m.dict )

    def test_10(self):
        "test dumps/loads"

        now = tznow()
        m1 = MyModel( int_type=3, str_type='string', dt_type=now )

        d = m1.dict
        self.assertTrue( d )

        m2 = MyModel( **d )

        self.assertDictEqual( m1.dict, m2.dict )
