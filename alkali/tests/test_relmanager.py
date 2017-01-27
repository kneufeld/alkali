import unittest

from alkali.model import Model
from alkali.relmanager import RelManager
from alkali import fields

class Entry(Model):
    date  = fields.DateTimeField(primary_key = True)

class Entry2(Model):
    date  = fields.DateTimeField(primary_key = True)

class AuxInfo(Model):
    entry     = fields.ForeignKey(Entry, primary_key=True)
    entry2    = fields.ForeignKey(Entry2)
    mime_type = fields.StringField()

class TestRelManager( unittest.TestCase ):

    def setUp(self):
        self.e = Entry(date='now').save()
        self.e2 = Entry2(date='now').save()
        self.a = AuxInfo(entry=self.e, entry2=self.e2).save()

    def tearDown(self):
        Entry.objects.clear()
        Entry2.objects.clear()
        AuxInfo.objects.clear()

    def test_init(self):
        self.assertTrue( str(self.e.auxinfo_set) )

    def test_1(self):

        e = self.e
        e2 = self.e2
        a = self.a

        # print e.auxinfo_set
        # print a.Meta.fields
        # print a.Meta.pk_fields
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

    def test_2(self):

        e = self.e
        e2 = self.e2
        a = e.auxinfo_set.create(mime_type='text/plain')

        self.assertEqual( a, e.auxinfo_set.get() )

        e2.auxinfo_set.add(a)
        self.assertEqual( a, e2.auxinfo_set.get() )
