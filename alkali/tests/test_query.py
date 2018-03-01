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
        m = MyModel(int_type=3, str_type='string', dt_type=now ).save()

        self.assertEqual( 0, len(q) )
        self.assertEqual( 0, q.count )
        self.assertEqual( 1, len(man) )

    def test_6(self):
        "make sure query length changes as we filter"
        for i in range(3):
            MyModel(int_type=i).save()

        q = MyModel.objects.all()
        self.assertEqual( 3, len(q) )

        q.filter(int_type__gt=0)
        self.assertEqual( 2, len(q) )

        q.filter(int_type__gt=1)
        self.assertEqual( 1, len(q) )

        q.filter(int_type__gt=2)
        self.assertEqual( 0, len(q) )

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

        self.assertEqual( man._instances[1].pk, q[0].pk )
        self.assertNotEqual( id(man._instances[1]), id(q[0]) )
        self.assertNotEqual( id(man._instances[1]), id(list(q)[0]) )

    def test_15(self):
        "make sure query objects are not 'updated' when manager objects changes"

        now = tznow()
        m = MyModel(int_type=3, str_type='string', dt_type=now ).save()

        man = MyModel.objects
        q = Query(man)

        mq = q[0]
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
            self.assertEqual( i, q[0].int_type )

    def test_21(self):
        "test different filter functions"

        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string %d' % i, dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        results = MyModel.objects.filter(int_type__eq=0)
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(int_type__gt=0)
        self.assertEqual( 2, len(results) )

        results = MyModel.objects.filter(int_type=0, str_type='string 0')
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(int_type=0, str_type='string XXX')
        self.assertEqual( 0, len(results) )

        results = MyModel.objects.filter(iter_type__in=[1])
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(iter_type__rin=1)
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(iter_type__rin=[1])
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(str_type__in=['string 1'])
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(str_type__rin='1')
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(str_type__re='1$')
        self.assertEqual( 1, len(results) )

        results = MyModel.objects.filter(str_type__rei='^STR')
        self.assertEqual( 3, len(results) )

        results = MyModel.objects.filter(dt_type__gt=fromts(0))
        self.assertEqual( 3, len(results) )

        # test pk queries
        results = MyModel.objects.filter(pk=1)
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

        results = MyMulti.objects.filter(pk=(1,2))
        self.assertEqual( 1, len(results) )

        results = MyMulti.objects.filter(pk=[1,2])
        self.assertEqual( 0, len(results) )

        results = MyMulti.objects.filter(pk=1)
        self.assertEqual( 0, len(results) )

        results = MyMulti.objects.filter(pk=(10,2))
        self.assertEqual( 1, len(results) )

        results = MyMulti.objects.filter(pk=(2,10))
        self.assertEqual( 0, len(results) )

        results = MyMulti.objects.filter(pk1=10)
        self.assertEqual( 2, len(results) )

    def test_35(self):
        "test order_by"

        # make some instances
        now = tznow()
        instances = [ MyModel(int_type=i, str_type='string', dt_type=now ).save() for i in range(3)]
        self.assertEqual( instances, list(MyModel.objects.all()) )

        self.assertEqual( Query, type(MyModel.objects.all().order_by('int_type')) )
        self.assertEqual( instances, list(MyModel.objects.all()) )

        self.assertEqual( instances[::-1], list( MyModel.objects.all().order_by('-int_type')) )
        self.assertEqual( instances, list(MyModel.objects.all().order_by('str_type','dt_type')) )

        self.assertEqual( instances, list(MyModel.objects.all().order_by('pk')) )

    def test_40(self):
        "test limit, equivalent to slicing"

        # for i in range(3):
        #     MyModel(int_type=i, str_type='string %d' % i, dt_type=now).save()
        now = tznow()
        instances = [MyModel(int_type=i, str_type='string %d' % i, dt_type=now ) for i in range(3)]

        for inst in instances:
            inst.save()

        # make sure all ids are unique
        ids = [id(instances[0]), id(MyModel.objects._instances[0]), id(MyModel.objects.get(0))]
        self.assertEqual(len(ids), len(set(ids)) )

        self.assertNotEqual( id(MyModel.objects._instances[0]), id(MyModel.objects.limit(0)[0]) )

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

        d = { 'int_type':1, 'str_type':u'string', 'dt_type':now }

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
        verify that lists are returned
        """
        for i in range(3):
            MyModel(int_type=i, str_type='string').save()

        q = MyModel.objects.all()
        self.assertEqual( 3, len(q.values_list()) )

        self.assertTrue( (0) in q.values_list()[0] )
        self.assertEqual( [(0)], q.values_list('int_type')[0] )

        for i in range(3):
            self.assertEqual( [i, u'string'], q.values_list('int_type', 'str_type')[i] )

    def test_value_list_1(self):
        """
        verify that flat lists are returned
        """
        for i in range(3):
            MyModel(int_type=i, str_type='string').save()

        q = MyModel.objects.all()
        self.assertEqual( 9, len(q.values_list(flat=True)) )
        self.assertEqual( 3, len(q.values_list('int_type', flat=True)) )

        self.assertTrue( 0 in q.values_list(flat=True) )
        self.assertEqual( [0,1,2], q.values_list('int_type', flat=True) )

        self.assertEqual( [0, u'string'],
                q.filter(int_type=0).values_list('int_type', 'str_type', flat=True) )

    def test_exists(self):
        for i in range(3):
            MyModel(int_type=i, str_type='string').save()

        q = MyModel.objects.all()

        self.assertTrue( q.filter(int_type=0).exists() )
        self.assertFalse( q.filter(int_type=9).exists() )

    def test_agg_sum(self):
        for i in range(1,4):
            MyModel(int_type=i, str_type='string').save()

        q = MyModel.objects.all()

        from alkali.query import Sum, Count, Max, Min

        d = {'int_type__sum': 6, 'str_type__count': 3}
        self.assertDictEqual( d, q.aggregate(Sum('int_type'), Count('str_type')) )

        d = {'foo': 6, 'bar': 3}
        self.assertDictEqual( d, q.aggregate(foo=Sum('int_type'), bar=Count('str_type')) )

        d = {'int_type__min': 1}
        self.assertDictEqual( d, q.aggregate(Min('int_type')) )

        d = {'int_type__max': 3}
        self.assertDictEqual( d, q.aggregate(Max('int_type')) )

    def test_annotate_1(self):
        "test hard-coded annotation"
        m = MyModel(int_type=0, str_type='string').save()
        q = MyModel.objects.all()

        a = q.annotate(foo='foo')[0]
        self.assertEqual( "foo", a.foo )
        self.assertFalse( hasattr(MyModel.objects._instances[0], 'foo') )

    def test_annotate_2(self):
        "test callable annotation"
        m = MyModel(int_type=1, str_type='string').save()
        q = MyModel.objects.all()

        def func(elem):
            return elem.str_type + " {}".format(elem.int_type)

        a = q.annotate(foo=func)[0]
        self.assertEqual( "string 1", a.foo )

    def test_distinct(self):
        MyModel(int_type=1, str_type='string').save()
        MyModel(int_type=2, str_type='string').save()

        self.assertEqual( [[1,2]], MyModel.objects.distinct('int_type') )
        self.assertEqual( [['string']], MyModel.objects.distinct('str_type') )
        self.assertEqual( [[1,2],['string']], MyModel.objects.distinct('int_type','str_type') )

    def test_first_1(self):
        m1 = MyModel(int_type=1, str_type='string').save()
        m2 = MyModel(int_type=2, str_type='string').save()

        self.assertEqual(m1, MyModel.objects.all().first())
        self.assertEqual(m1, MyModel.objects.filter(int_type=1).first())

    def test_first_2(self):
        with self.assertRaises(MyModel.DoesNotExist):
            MyModel.objects.first()

    def test_sorted(self):
        """
        make sure we get our models back in sorted order
        not actually sure this works on purpose or by accident
        """
        MyModel(int_type=4).save()
        MyModel(int_type=9).save()
        MyModel(int_type=2).save()
        MyModel(int_type=3).save()
        MyModel(int_type=1).save()
        MyModel(int_type=5).save()
        MyModel(int_type=6).save()
        MyModel(int_type=10).save()
        MyModel(int_type=8).save()
        MyModel(int_type=7).save()

        q = MyModel.objects.all()

        for i in range(10):
            self.assertEqual(i + 1, q[i].int_type)

    def test_groupby_1(self):
        MyModel(int_type=1, str_type='string 1').save()
        MyModel(int_type=2, str_type='string 1').save()
        MyModel(int_type=3, str_type='string 2').save()

        q = MyModel.objects.filter(**{'int_type': 1})
        self.assertEqual( 1, q[0].int_type)

        q = MyModel.objects.all()
        self.assertEqual( 3, len(q) )

        groups = MyModel.objects.group_by('str_type')

        expected = {
            'string 1': [1, 2],
            'string 2': [3],
        }

        self.assertEqual(set(expected.keys()), set(groups.keys()))

        g1 = groups['string 1'].all().order_by('int_type').values_list('int_type', flat=True)
        self.assertEqual(set(expected['string 1']), set(g1))

        g2 = groups['string 2'].all().order_by('int_type').values_list('int_type', flat=True)
        self.assertEqual(set(expected['string 2']), set(g2))
