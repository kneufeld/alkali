import unittest

from alkali.query import Query
from alkali import tznow, fromts

from . import MyModel, MyMulti

class TestQuery( unittest.TestCase ):

    def tearDown(self):
        MyModel.objects.clear()

    def test_1(self):
        "verify class/instance implementation"
        q = Query(MyModel.objects)
        self.assertTrue( str(q) )

    def test_2(self):
        "make sure Manager is returning a query object"
        man = MyModel.objects
        self.assertEqual( Query, type(man.filter()) )

    def test_3(self):
        "make sure field helpers work"
        q = Query(MyModel.objects)
        self.assertTrue( 'int_type' in q.field_names )
        self.assertTrue( 'str_type' in q.field_names )
        self.assertTrue( 'dt_type' in q.field_names )

    def test_5(self):
        "make sure query doesn't change after manager does"

        man = MyModel.objects
        q = Query(man)
        self.assertEqual( 0, len(q) )

        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now )
        m.save()

        self.assertEqual( 0, len(q) )
        self.assertEqual( 0, q.count )
        self.assertEqual( 1, len(man) )

    def test_10(self):
        "make sure query gets instances"

        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now )
        m.save()

        man = MyModel.objects
        q = Query(man)

        self.assertEqual( 1, len(man) )
        self.assertEqual( 1, len(q) )
        self.assertEqual( m, q[0] )

    def test_11(self):
        "make sure query gets a copy of model instances"
        m = MyModel(int_type=1).save()

        man = MyModel.objects
        q = Query(man)

        self.assertEqual( man._instances[1].pk, q.instances[0].pk )
        self.assertNotEqual( id(man._instances[1]), id(q.instances[0]) )

    def test_15(self):
        "make sure query objects are not 'updated' when manager objects changes"

        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now ).save()

        man = MyModel.objects
        q = Query(man)

        mq = q.instances[0]
        self.assertEqual( m.str_type, mq.str_type )

        m.str_type = 'new string'
        self.assertNotEqual( m.str_type, mq.str_type )

    def test_20(self):
        "test filter function"
        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        for i in range(3):
            q = MyModel.objects.filter(int_type=i)
            self.assertEqual( 1, len(q) )
            self.assertEqual( i, q.instances[0].int_type )

    def test_21(self):
        "test different filter functions"

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string %d' % i, dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        results = MyModel.objects.filter(int_type__eq=0).instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(int_type__gt=0).instances
        self.assertEqual( 2, len(results) )

        results = MyModel.objects.filter(int_type=0, str_type='string 0').instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(int_type=0, str_type='string XXX').instances
        self.assertEqual( 0, len(results) )

        results = MyModel.objects.filter(iter_type__in=[1]).instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(iter_type__rin=1).instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(iter_type__rin=[1]).instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(str_type__in=['string 1']).instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(str_type__rin='1').instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(str_type__re='1$').instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(str_type__rei='^STR').instances
        self.assertEqual( 3, len(results) )

        results = MyModel.objects.filter(dt_type__gt=fromts(0)).instances
        self.assertEqual( 3, len(results) )

        # test pk queries
        results = MyModel.objects.filter(pk=1).instances
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.get(pk=1)
        self.assertEqual( MyModel, type(results) )

    def test_25(self):
        "test chaining filters together"

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        q = MyModel.objects.filter(int_type__gt=0).filter(int_type=1)
        self.assertEqual( 1, len(q) )

    def test_30(self):
        "test query iteration"

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        q = MyModel.objects.filter()
        c = 0
        for i in q:
            c += 1

        self.assertEqual( 3, c )

    def test_31(self):
        "test pk searching with multiple primary keys"
        m1 = MyMulti(pk1=1,pk2=2,other='1 2')
        m1.save()
        m2 = MyMulti(pk1=10,pk2=2,other='10 2')
        m2.save()
        m3 = MyMulti(pk1=10,pk2=3,other='10 3')
        m3.save()

        results = MyMulti.objects.filter(pk=(1,2)).instances
        self.assertEqual( 1, len(results) )

        results = MyMulti.objects.filter(pk=[1,2]).instances
        self.assertEqual( 0, len(results) )

        results = MyMulti.objects.filter(pk=1).instances
        self.assertEqual( 0, len(results) )

        results = MyMulti.objects.filter(pk=(10,2)).instances
        self.assertEqual( 1, len(results) )

        results = MyMulti.objects.filter(pk=(2,10)).instances
        self.assertEqual( 0, len(results) )

        results = MyMulti.objects.filter(pk1=10).instances
        self.assertEqual( 2, len(results) )

    def test_35(self):
        "test order_by"

        # make some instances
        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ) for i in range(3)]
        map( lambda e: e.save(), instances )
        self.assertEqual( instances, MyModel.objects.all().instances )

        self.assertEqual( Query, type(MyModel.objects.all().order_by('int_type')) )
        self.assertEqual( instances, MyModel.objects.all().instances )

        self.assertEqual( instances[::-1], MyModel.objects.all().order_by('-int_type').instances )
        self.assertEqual( instances, MyModel.objects.all().order_by('str_type','dt_type').instances )

        self.assertEqual( instances, MyModel.objects.all().order_by('pk').instances )

    def test_40(self):
        "test limit, equivalent to slicing"

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string %d' % i, dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        self.assertEqual( list, type(MyModel.objects.all().limit(0)) )
        self.assertEqual( 3, len(MyModel.objects.all().limit(0)) )

        self.assertEqual( 2, len(MyModel.objects.all().limit(2)) )
        self.assertEqual( 2, len(MyModel.objects.all().limit(-2)) )

        self.assertEqual( instances[:2], MyModel.objects.all().limit(2) )
        self.assertEqual( instances[-2:], MyModel.objects.all().limit(-2) )

    def test_values(self):
        """
        test .values(), return dict instead of objects
        """
        now = tznow()
        m = MyModel(int_type=1, str_type=u'string', dt_type=now).save()

        d = { 'int_type':1, 'str_type':u'string', 'dt_type':now.isoformat() }

        self.assertDictEqual( d, m.dict ) # quick test to so we know what we're working with

        q = MyModel.objects.all()

        self.assertDictEqual( d, q.values()[0] )
        self.assertDictEqual(
                { 'int_type':1, 'str_type':u'string' },
                q.values('int_type', 'str_type' )[0] )
        self.assertDictEqual(
                { 'str_type':u'string' },
                q.values('str_type' )[0] )

    def test_values_1(self):
        """
        test .values() with multiple returned values
        """
        for i in range(3):
            MyModel(int_type=i).save()

        q = MyModel.objects.all()
        self.assertEqual( 3, len(q.values()) )

        for i in range(3):
            self.assertDictEqual( {'int_type':i}, q.values('int_type')[i] )

    def test_value_list(self):
        """
        verify that lists are returne
        """
        for i in range(3):
            MyModel(int_type=i).save()

        q = MyModel.objects.all()
        self.assertEqual( 3, len(q.values_list()) )

        self.assertTrue( ('int_type', 0) in q.values_list()[0] )
        self.assertEqual( [('int_type', 0)], q.values_list('int_type')[0] )
