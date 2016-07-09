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
        "make sure date gets a timezone"
        now = dt.datetime.now() # no timezone
        d = DateField( now )
        now = tzadd(now)
        self.assertEqual( now, d.value )

    def test_3(self):
        "make sure date keeps timezone"
        now = tznow()
        d = DateField( now )
        self.assertEqual( now, d.value )

    def test_4(self):
        "test primary key setting"
        f = IntField( 1 )
        self.assertEqual( False, f.primary_key )

        f = IntField( 1, primary_key=True )
        self.assertEqual( True, f.primary_key )

    def test_5(self):
        "test modified flag"
        f = IntField( 1 )
        self.assertEqual( False, f.modified )

        f.value = 1
        self.assertEqual( True, f.modified )

        # datefield has it's own setter so test it too
        f = DateField( tznow() )
        f.value = tznow()
        self.assertEqual( True, f.modified )
