import os
import unittest
from zope.interface.verify import verifyObject, verifyClass

from alkali.model import IModel, Model
from alkali import fields
from alkali import tznow
from . import EmptyModel, MyModel, MyMulti

class TestModel( unittest.TestCase ):

    def tearDown(self):
        MyModel.objects.clear()

    def test_1(self):
        "verify class/instance implementation"

        for model_class in [EmptyModel, MyModel]:
            self.assertTrue( verifyClass(IModel, model_class) )
            m = model_class()
            self.assertTrue( verifyObject(IModel, m) )

            self.assertTrue( m.dict or m.dict == {} ) # make sure it doesn't blow up
            self.assertTrue( m.schema ) # make sure it doesn't blow up
            self.assertTrue( m.json ) # make sure it doesn't blow up

        m = EmptyModel(foo='bar')
        self.assertEqual( 'bar', m.foo )

        self.assertTrue( EmptyModel.objects != MyModel.objects )


    def test_2(self):
        "empty fields by default"
        self.assertEqual( 0, len(EmptyModel.Meta.fields) )

    def test_3(self):
        "lets make some fields"
        m = MyModel()
        self.assertEqual( 3, len(m.Meta.fields) )
        self.assertEqual( 3, len(MyModel.Meta.fields) )

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
        "test dirty flag"

        m = MyModel()
        self.assertFalse( m.dirty )

        m = MyModel(int_type=1)
        self.assertFalse( m.dirty )

    def test_6a(self):
        "test dirty flag"

        m = MyModel()

        m.int_type = 1
        self.assertTrue( m.dirty )

        m.save()
        self.assertFalse( m.dirty )

    def test_7(self):
        "find the primary key"
        m=MyModel(int_type=1)
        self.assertEqual( 1, m.int_type )
        self.assertEqual( m.int_type, m.pk )

        n=MyModel(int_type=2)
        #print id(m.Meta.fields['int_type']), id(n.Meta.fields['int_type'])

    def test_8(self):
        "find the filename and str"
        m=MyModel()
        self.assertTrue( m.__class__.__name__ in str(m) )

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

    def test_11(self):
        "test save to manager"

        self.assertEqual(0, len(MyModel.objects) )

        now = tznow()
        m1 = MyModel( int_type=3, str_type='string', dt_type=now )

        m1.save()
        self.assertEqual(1, len(MyModel.objects) )

        m1.str_type = 'new string'
        m1.save()
        self.assertEqual(1, len(MyModel.objects) )

    def test_15(self):
        "test setting/casting"
        m = MyModel()

        with self.assertRaises( ValueError ):
            m.int_type = "abc"

        m.int_type = "1"
        self.assertEqual( 1, m.int_type )
        self.assertEqual( int, type(m.int_type) )

    def test_16(self):
        "test equality"
        m1 = MyModel(int_type=1)
        m2 = MyModel(int_type=1)

        self.assertTrue( id(m1) != id(m2) )
        self.assertEqual( m1, m2 )
        self.assertFalse( m1 != m2 )

    def test_17(self):
        "test meta ordering"

        with self.assertRaises( AssertionError):
            class MyMulti(Model):
                class Meta:
                    ordering = ['f1','f2']

                f1 = fields.IntField()
                f2 = fields.IntField()
                other = fields.StringField()

    def test_18(self):
        "test multi field primary key"
        self.assertTrue( verifyClass(IModel, MyMulti) )
        m = MyMulti(pk1=100,pk2=200)
        self.assertTrue( verifyObject(IModel, m) )
        self.assertTrue( m.schema )

        self.assertEqual( ['pk1','pk2'], MyMulti.Meta.pk_fields )
        self.assertEqual( (100,200), m.pk )
