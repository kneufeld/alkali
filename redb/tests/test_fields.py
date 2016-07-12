import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt

from redb.fields import IField, Field, IntField, StringField, DateField
from redb import tznow, tzadd

class TestField( unittest.TestCase ):

    def test_1(self):
        "verify class/instance implementation"
        self.assertTrue( verifyClass(IField, Field) )

        for field in [IntField, StringField, DateField]:
            self.assertTrue( verifyClass(IField, field) )
            f = field()
            self.assertTrue( verifyObject(IField, f) )

    def test_2(self):
        "Field is a meta class, it has no value. make sure of that"
        f = IntField( 1 )
        with self.assertRaises(AttributeError):
            f.value
        with self.assertRaises(AttributeError):
            f._value

    def test_4(self):
        "test primary key setting"
        f = IntField( 1 )
        self.assertEqual( False, f.primary_key )

        f = IntField( 1, primary_key=True )
        self.assertEqual( True, f.primary_key )
