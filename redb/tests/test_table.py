import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.table import ITable, Table
from redb import fields
from redb import tznow

class MyTable( Table ):
    int_type = fields.IntField()
    str_type = fields.StringField()
    dt_type  = fields.DateField()

class TestTable( unittest.TestCase ):

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(ITable, Table) )

        t = Table()
        self.assertTrue( verifyObject(ITable, t) )

    def test_2(self):
        "empty fields by default"
        t = Table()
        self.assertEqual( 0, len(t.fields) )

    def test_3(self):
        "lets make some fields"
        t = MyTable()
        self.assertEqual( 3, len(t.fields) )
        self.assertEqual( "MyTable", t.name )

    def test_4(self):
        "lets set some fields"
        now = tznow()
        t = MyTable(int_type=3, str_type='string', dt_type=now )
        self.assertEqual( 3, t.fields['int_type'].value )
        self.assertEqual( 'string', t.fields['str_type'].value )
        self.assertEqual( now, t.fields['dt_type'].value )

    def test_5(self):
        "lets make a few instances to make sure there are no overwrites"
        t0 = MyTable()
        self.assertTrue( t0.int_type )
        self.assertIsNone( t0.int_type.value )

        t1 = MyTable(int_type=1)
        t2 = MyTable(int_type=2)

        self.assertEqual( 1, t1.fields['int_type'].value )
        self.assertEqual( 2, t2.fields['int_type'].value )
