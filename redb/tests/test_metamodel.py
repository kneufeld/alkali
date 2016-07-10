import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.database import IDatabase, Database
from redb.model import IModel, Model
from redb.metamodel import MetaModel
from redb.storage import JSONStorage
from redb import fields
from redb import tznow
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

        m = MyModel()
        self.assertEqual( MyModel.Meta.ordering, m.fields.keys() )

    def test_4(self):
        "verify that Model.objects exists/works (a ModelManager)"

        now = tznow()
        m1 = MyModel( int_type=3, str_type='string', dt_type=now )

        MyModel.objects.save(m1)

        m2 = m1.objects.get(m1.pk)
        self.assertDictEqual( m1.dict, m2.dict )
