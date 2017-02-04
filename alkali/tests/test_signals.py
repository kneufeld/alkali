import unittest
import mock
import blinker

from alkali import signals
from . import MyModel

class TestSignals( unittest.TestCase ):

    def setUp(self):
        pass

    def tearDown(self):
        MyModel.objects.clear()

    def test_blinker(self):
        # a few tests so we know how blinker works
        self.assertEqual( signals.creation, blinker.signal('creation') )

        # subscribe
        signals.creation.connect( lambda instance: None )

    def test_instance_creation(self):

        created = mock.Mock()

        with signals.creation.connected_to(created.cb):
            MyModel(int_type=1).save()
            created.cb.assert_called()

    def test_instance_delete(self):

        pre = mock.Mock()
        post = mock.Mock()

        with signals.pre_delete.connected_to(pre.cb):
            with signals.post_delete.connected_to(post.cb):
                m = MyModel(int_type=1).save()
                MyModel.objects.delete(m)
                pre.cb.assert_called_once()
                post.cb.assert_called_once()

    def test_instance_save(self):

        pre = mock.Mock()
        post = mock.Mock()

        with signals.pre_save.connected_to(pre.cb):
            with signals.post_save.connected_to(post.cb):
                MyModel(int_type=2).save()
                pre.cb.assert_called_once()
                post.cb.assert_called_once()
