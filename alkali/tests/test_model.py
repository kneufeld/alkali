import os
import unittest
from zope.interface.verify import verifyObject, verifyClass

from alkali.model import Model
from alkali import fields
from alkali import tznow
from . import EmptyModel, MyModel, MyMulti

class TestModel( unittest.TestCase ):

    def tearDown(self):
        MyModel.objects.clear()

    def test_1(self):
        "verify class/instance implementation"

        for model_class in [EmptyModel, MyModel]:
            m = model_class()

            self.assertTrue( m.dict or m.dict == {} ) # make sure it doesn't blow up
            self.assertTrue( m.schema ) # make sure it doesn't blow up
            self.assertTrue( m.json ) # make sure it doesn't blow up

        m = EmptyModel(foo='bar')
        self.assertEqual( 'bar', m.foo )

        self.assertTrue( EmptyModel.objects != MyModel.objects )
        self.assertTrue( EmptyModel.objects is not MyModel.objects )

        self.assertTrue( EmptyModel.pk )

        m1 = MyModel(int_type=1)
        m2 = MyModel(int_type=2)
        self.assertEqual( id(m1.Meta), id(m2.Meta) )

        self.assertEqual( id(m1.Meta.fields['int_type']), id(m2.int_type__field) )

    def test_2(self):
        "empty fields by default"
        self.assertEqual( 0, len(EmptyModel.Meta.fields) )
        self.assertEqual( 0, len(EmptyModel().Meta.fields) )

    def test_3(self):
        "lets make some fields"
        m = MyModel()
        self.assertEqual( 3, len(m.Meta.fields) )
        self.assertEqual( 3, len(MyModel.Meta.fields) )

        self.assertEqual( None, m.int_type )
        self.assertEqual( None, m.str_type )
        self.assertEqual( None, m.dt_type )

    def test_3a(self):
        "test that memoized_property works"
        m = MyModel()
        self.assertEqual( None, m.pk )
        self.assertEqual( None, m.pk )
        m.int_type = 1
        self.assertEqual( 1, m.pk )
        self.assertEqual( 1, m.pk )

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
        self.assertFalse( m.dirty )

        m.int_type = 1
        self.assertTrue( m.dirty )

        m.save()
        self.assertFalse( m.dirty )

    def test_7(self):
        "find the primary key"
        m=MyModel(int_type=1)
        self.assertEqual( 1, m.int_type )
        self.assertEqual( m.int_type, m.pk )
        self.assertTrue( m.int_type__field.primary_key )

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
        m = MyMulti(pk1=100,pk2=200)
        self.assertTrue( m.schema )

        self.assertEqual( ['pk1','pk2'], MyMulti.Meta.pk_fields.keys() )
        self.assertEqual( (100,200), m.pk )

    def test_20(self):
        "test that get() object doesn't affect saved object"

        m1 = MyModel(int_type=1)
        m1.save()

        c = MyModel.objects.get(1)
        self.assertEqual(m1.pk, c.pk)

        c.str_type = "new value"
        self.assertTrue(c.dirty)
        self.assertFalse(m1.dirty)
        self.assertNotEqual(m1.str_type, c.str_type)
        self.assertEqual(m1.int_type, c.int_type)

        # c is now the "true" object in its manager
        c.save()
        self.assertNotEqual( id(c), id(MyModel.objects._instances[c.int_type]) )
        self.assertNotEqual( id(c), id(m1) )

    def test_doesnotexist(self):
        self.assertEqual( MyModel.ObjectDoesNotExist, MyMulti.ObjectDoesNotExist )
        self.assertNotEqual( MyModel.DoesNotExist, MyMulti.DoesNotExist )
