import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.table import ITable, Table
from redb import fields

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
        class MyTable( Table ):
            int_type = fields.IntField()
            str_type = fields.StringField()
            dt_type  = fields.DateField()

        t = MyTable()
        self.assertEqual( 3, len(t.fields) )
        self.assertEqual( "MyTable", t.name )
