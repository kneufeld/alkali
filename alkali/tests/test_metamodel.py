import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from alkali.database import Database
from alkali.model import Model
from alkali.metamodel import MetaModel
from alkali.storage import JSONStorage
from alkali import fields
from alkali import tznow
from . import MyModel

curr_dir = os.path.dirname( os.path.abspath( __file__ ) )

class TestMetaModel( unittest.TestCase ):

    def test_1(self):
        "verify attributes on class, not instance"

        cls = MyModel
        self.assertTrue( hasattr(cls, 'objects') )
        self.assertTrue( hasattr(cls, 'Meta') )
        self.assertTrue( hasattr(cls.Meta, 'fields') )

    def test_2(self):
        "verify attributes on class, not instance"

        class EmptyModel(Model):
            pass

        cls = EmptyModel
        self.assertTrue( hasattr(cls, 'objects') )
        self.assertTrue( hasattr(cls, 'Meta') )
        self.assertTrue( hasattr(cls.Meta, 'fields') )

    def test_3(self):
        "verify that Meta.ordering works"
        self.assertEqual( MyModel.Meta.ordering, list(MyModel.Meta.fields.keys()) )

    def test_4(self):
        "verify that Model.objects exists/works (a ModelManager)"

        now = tznow()
        m1 = MyModel( int_type=3, str_type='string', dt_type=now )

        MyModel.objects.save(m1)

        m2 = m1.objects.get(m1.pk)
        self.assertDictEqual( m1.dict, m2.dict )

    def test_5(self):
        "verify meta.fields and meta.pk_fields"

        self.assertEqual( 3, len(MyModel.Meta.fields) )
        self.assertEqual( 'int_type', list(MyModel.Meta.pk_fields.keys())[0] )
