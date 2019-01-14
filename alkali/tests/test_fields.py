# -*- coding: utf-8 -*-
# "ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ"

import unittest
import mock
import datetime as dt
import json
import tempfile

from alkali.fields import Field
from alkali.fields import IntField, StringField, BoolField
from alkali.fields import DateTimeField, FloatField, SetField
from alkali.fields import UUIDField
from alkali.fields import ForeignKey, OneToOneField
from alkali.model import Model

from . import MyModel, MyMulti, MyDepModel, AutoModel1

class TestField( unittest.TestCase ):

    def tearDown(self):
        MyModel.objects.clear()
        MyMulti.objects.clear()
        MyDepModel.objects.clear()

    def test_1(self):
        "verify class/instance implementation"

        for field in [IntField, BoolField, StringField, DateTimeField, FloatField, SetField ]:
            f = field()
            self.assertTrue( str(f) )
            self.assertTrue( f.properties )

        f = ForeignKey(MyModel)
        self.assertTrue( str(f) )

        m1 = MyModel(int_type=1)
        m2 = MyModel(int_type=2)
        self.assertEqual( id(m1.Meta.fields['int_type']), id(m2.Meta.fields['int_type']) )

    def test_2(self):
        "Field is a meta-like class, it has no value. make sure of that"
        f = IntField()
        with self.assertRaises(AttributeError):
            f.value
        with self.assertRaises(AttributeError):
            f._value

    def test_4(self):
        "test some field properties, verify primary key setting"
        f = IntField()

        for prop in f.properties:
            self.assertFalse( getattr(f, prop) )

        f = IntField( primary_key=True, indexed=True )
        self.assertEqual( True, f.primary_key )
        self.assertEqual( True, f.indexed )

    def test_5(self):
        "test date setting"
        now = dt.datetime.now()
        f = DateTimeField()
        v = f.cast(now)

        self.assertIsNotNone( v.tzinfo )

        v = f.cast(v) # keeps tzinfo
        self.assertIsNotNone( v.tzinfo )

        v = f.cast('now')
        self.assertEqual( dt.datetime, type(v) )

        v = f.loads('2016-07-20 17:53')
        self.assertEqual( dt.datetime, type(v) )

        self.assertRaises( TypeError, f.cast, 1 )

    def test_6(self):
        "test SetField"
        s = set([1, 2, 3])
        f = SetField()

        v = f.cast(s)
        self.assertEqual( s, v )

        self.assertEqual( s, f.loads( f.dumps(s) ) )

    def test_7(self):
        "test StringField"
        s = "ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ"

        f = StringField()

        v = f.cast(s)
        self.assertEqual( s, v )
        self.assertEqual( v, f.loads( f.dumps(v) ) )

    def test_int_into_stringfield(self):
        f = StringField()
        v = f.cast(1)
        self.assertEqual( str(1), v )

    def test_8(self):
        "test none/null"
        f = DateTimeField()

        v = f.loads(None)
        self.assertIsNone(v)

        v = f.loads('null')
        self.assertIsNone(v)

    def test_10(self):
        "test foreign keys, link to multi pk model not supported"
        with self.assertRaises(AssertionError):
            class MyDepModelMulti(Model):
                pk1     = IntField(primary_key=True)
                foreign = ForeignKey(MyMulti)

        # can't name field pk
        with self.assertRaises(AssertionError):
            class MyDepModel(Model):
                pk      = IntField(primary_key=True)
                foreign = ForeignKey(MyModel)

    def test_11(self):
        """
        test foreign keys
        note: just being able to define MyDepModel runs lots of code
        """
        m = MyModel(int_type=1).save()
        self.assertFalse( m.mydepmodel_set.all() )

        d = MyDepModel(pk1=1, foreign=m)
        self.assertTrue( isinstance(d.foreign, MyModel) )
        self.assertNotEqual( id(m), id(d.foreign) ) # d.foreign gets a copy of the object

        d = MyDepModel(pk1=1, foreign=1) # foreign key value
        self.assertTrue( isinstance(d.foreign, MyModel) )
        self.assertNotEqual( id(m), id(d.foreign) )

        d.foreign.str_type = "hello world"
        self.assertNotEqual( "hello world", m.str_type )

        # after locally storing a version of m, modify and save and get it back
        m2 = d.foreign
        m2.str_type = "hello world"
        m2.save()
        self.assertEqual( "hello world", d.foreign.str_type )

        self.assertNotEqual( m.str_type, m2.str_type )

    def test_12(self):
        "test save"
        m = MyModel(int_type=1).save()
        MyDepModel(pk1=1, foreign=m).save()

    def test_12a(self):
        "test that trying to save unset foreign key fails"

        m = MyDepModel(pk1=1)
        with self.assertRaises(RuntimeError):
            m.dict

        # FIXME this should probably happen
        # with self.assertRaises(RuntimeError):
        #     m.save()

        f = MyModel(int_type=1).save()
        m.foreign = f

        self.assertTrue(m.dict)

    def test_13(self):
        """
        test queries
        """
        m = MyModel(int_type=1).save()
        d = MyDepModel(pk1=10, foreign=m).save()

        self.assertEqual( m, d.foreign )

        # filters on MyDepModel "obviously" return MyDepModel even if
        # we're comparing with foreign keys
        self.assertEqual( d, MyDepModel.objects.get(foreign=m) )
        self.assertEqual( d, MyDepModel.objects.filter(foreign=m)[0] )

    def test_14(self):
        "test extra kw params to field raise assertion"
        with self.assertRaises(AssertionError):
            IntField(some_keyword=True)

    def test_15(self):
        """
        test *_set on foreign model
        """
        m = MyModel(int_type=1).save()
        d = MyDepModel(pk1=10, foreign=m).save()

        self.assertTrue( hasattr( m, 'mydepmodel_set') )
        self.assertTrue( d in m.mydepmodel_set.all() )

    def test_16(self):
        "test some foreignkey casting"
        m = MyModel(int_type=1).save()
        MyDepModel(pk1=10, foreign=m).save()
        MyDepModel(pk1=11, foreign=1).save()
        MyDepModel(pk1=12, foreign="1").save()

        self.assertEqual( 3, m.mydepmodel_set.all().count )

    def test_20(self):
        "test auto increment integer field"

        class AutoModel1( Model ):
            auto = IntField(primary_key=True, auto_increment=True)

        class AutoModel2( Model ):
            auto = IntField(primary_key=True, auto_increment=True)

        self.assertEqual( 1, AutoModel1().auto )
        self.assertEqual( 2, AutoModel1().auto )

        self.assertEqual( 1, AutoModel2().auto )
        self.assertEqual( 2, AutoModel2().auto )

        m = AutoModel2().save()
        self.assertEqual( 3, m.auto )

    def test_auto_now(self):
        class AutoModel1( Model ):
            auto = IntField(primary_key=True, auto_increment=True)
            modified = DateTimeField(auto_now=True)
            other = IntField()

        m = AutoModel1()
        curr = m.modified
        self.assertNotEqual(None, curr)

        m.other = 2
        self.assertNotEqual(curr, m.modified)

    def test_auto_now_add(self):
        class AutoModel1( Model ):
            auto = IntField(primary_key=True, auto_increment=True)
            creation = DateTimeField(auto_now_add=True)
            other = IntField()

        m = AutoModel1()
        curr = m.creation
        self.assertNotEqual(None, curr)

        m.other = 2
        self.assertEqual(curr, m.creation)

    def test_25(self):
        "test that Field.__set__ gets called"

        with mock.patch.object(Field, '__set__') as mock_method:
            m = MyModel()
            m.int_type = 1
            mock_method.assert_called_once_with(m, 1)

        m = MyModel()
        self.assertIsNone( m.int_type )

        m.int_type = 1
        self.assertIsInstance( m.int_type, int )
        self.assertIsInstance( m.__dict__['int_type'], int )
        self.assertIs( m.int_type, m.__dict__['int_type'] )
        self.assertIsInstance( m.Meta.fields['int_type'], IntField ) # hasn't magically changed

    def test_26(self):
        "test that Field.__get__ gets called"

        with mock.patch.object(Field, '__get__') as mock_method:
            m = MyModel()
            m.int_type
            mock_method.assert_called_once_with(m.Meta.fields['int_type'], m, MyModel)

    def test_27(self):
        "test that magic model.fieldname_field returns Field object"
        m = MyModel()
        self.assertIs( MyModel.Meta.fields['int_type'], m.int_type__field )

    def test_28(self):
        # this is just to get code coverage, not sure how this
        # would ever happen in real life
        MyModel.int_type
        MyDepModel.foreign

    def test_30(self):
        "test BoolField"

        class MyModel( Model ):
            int_type   = IntField(primary_key=True)
            bool_type  = BoolField()

        m = MyModel()

        for v in [None, '']:
            m.bool_type = v
            self.assertEqual(None, m.bool_type)

        for v in ['false', 'False', '0', 'NO', 'n', 0, []]:
            m.bool_type = v
            self.assertEqual(False, m.bool_type)

        for v in [' ', 'true', 'anything else', 1, [1]]:
            m.bool_type = v
            self.assertEqual(True, m.bool_type)

    def test_valid_pk(self):
        import pytz
        from . import Entry
        now = dt.datetime.now(pytz.utc)
        e = Entry(pk=now)

        self.assertEqual(now, e.pk)
        self.assertTrue(e.valid_pk)

    def test_valid_pk_2(self):
        m = MyMulti(pk1=1, pk2=2).save()
        self.assertTrue(m.valid_pk)

    def test_one2one_sync(self):
        # need to define this inside test otherwise it will sync with
        # all other tests
        from . import Entry
        from alkali import signals as S

        self.assertFalse(S.creation.has_receivers_for(Entry))

        class AuxInfoSync(Model):
            entry     = OneToOneField(Entry, primary_key=True)
            mime_type = StringField()

        self.assertTrue(S.post_save.has_receivers_for(Entry))
        self.assertTrue(S.pre_delete.has_receivers_for(Entry))

        now = dt.datetime.now()
        e = Entry(pk=now)
        self.assertEqual(0, Entry.objects.count)
        self.assertEqual(0, AuxInfoSync.objects.count)

        e.save()
        self.assertEqual(1, Entry.objects.count)
        self.assertEqual(1, AuxInfoSync.objects.count)
        self.assertEqual(1, e.auxinfosync_set.count)

        Entry.objects.delete(e)
        self.assertEqual(0, AuxInfoSync.objects.count)

        del e
        self.assertEqual(0, AuxInfoSync.objects.count)

    def test_uuid(self):
        class AutoModel1(Model):
            auto = IntField(primary_key=True, auto_increment=True)
            uuid = UUIDField()

        m = AutoModel1()
        self.assertEqual(str, type(m.uuid))
        self.assertEqual(32 + 4, len(m.uuid)) # hex plus dashes
        self.assertNotEqual(m.uuid, AutoModel1().uuid) # hope this never fires...

    def test_uuid_creation_with_value(self):
        class AutoModel1(Model):
            auto = IntField(primary_key=True, auto_increment=True)
            uuid = UUIDField()

        uuid = '3533c123-3334-4a74-85f9-0f04ed034c53'
        m = AutoModel1(uuid=uuid)
        self.assertEqual(uuid, m.uuid)

    def test_uuid_read_only(self):
        class AutoModel1(Model):
            auto = IntField(primary_key=True, auto_increment=True)
            uuid = UUIDField()

        m = AutoModel1()
        self.assertTrue(m.uuid)

        with self.assertRaises(RuntimeError):
            m.uuid = "abc"

    def test_date_load_with_autotime(self):
        """
        make sure when we load a record that has auto_now or auto_now_add
        that the value in the file is used
        """
        tfile = tempfile.NamedTemporaryFile()

        data = b"""[{
            "auto": 5,
            "creation": "2010-01-13T17:52:09.131085-07:00",
            "modified": "2010-01-13T17:52:09.131178-07:00",
            "f1": "a value",
            "f2": null
            }]"""

        tfile.write(data)
        tfile.flush()

        creation = dt.datetime.fromisoformat("2010-01-13T17:52:09.131085-07:00")
        modified = dt.datetime.fromisoformat("2010-01-13T17:52:09.131178-07:00")

        from alkali.storage import JSONStorage
        storage = JSONStorage(tfile.name)
        AutoModel1.objects.load(storage)
        m = AutoModel1.objects.instances[0]

        self.assertEqual(creation, m.creation)
        self.assertEqual(modified, m.modified)
