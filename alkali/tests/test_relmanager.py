import os
import unittest
import tempfile
from zope.interface.verify import verifyObject, verifyClass
import datetime as dt
import json

from alkali.model import Model
from alkali.manager import IManager, Manager
from alkali.storage import JSONStorage
from alkali.query import Query
from alkali import fields
from alkali import tznow

from . import EmptyModel, MyModel

class Entry(Model):
    date  = fields.DateTimeField(primary_key = True)

class Entry2(Model):
    date  = fields.DateTimeField(primary_key = True)

class AuxInfo(Model):
    entry     = fields.ForeignKey(Entry, primary_key=True)
    entry2    = fields.ForeignKey(Entry2)
    mime_type = fields.StringField()

class TestRelManager( unittest.TestCase ):

    def tearDown(self):
        Entry.objects.clear()
        AuxInfo.objects.clear()

    def test_1(self):

        e = Entry(date='now').save()
        e2 = Entry2(date='now').save()
        a = AuxInfo(entry=e, entry2=e2).save()

        # print e.auxinfo_set
        # print a.meta.fields
        # print a.meta.pk_fields
        # print "pk",a.pk

        self.assertEqual(e, e.auxinfo_set.foreign)
        self.assertEqual(e2, e2.auxinfo_set.foreign)

        self.assertEqual(AuxInfo, e.auxinfo_set.child_class)
        self.assertEqual(AuxInfo, e2.auxinfo_set.child_class)

        self.assertEqual('entry', e.auxinfo_set.child_field)
        self.assertEqual('entry2', e2.auxinfo_set.child_field)

        self.assertEqual(e, a.entry)
        self.assertEqual(e2, a.entry2)

        self.assertEqual(a, e.auxinfo_set.get())
        self.assertEqual(a, e2.auxinfo_set.get())

        self.assertTrue( e.auxinfo_set.all())
        self.assertTrue( e2.auxinfo_set.all())
