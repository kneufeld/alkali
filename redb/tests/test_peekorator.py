"""
see ../peekorator.py for attribution
"""

from mock import Mock
from unittest import TestCase

from ..peekorator import peek, Peekorator

class TestPeek(TestCase):

    @staticmethod
    def throwing_peekorator(*args, **kwargs):
        raise StopIteration

    def test_calls_peek(self):
        fake_peekorator = Mock()
        fake_peekorator.__peek__ = Mock()
        peek(fake_peekorator)
        fake_peekorator.__peek__.assert_called_once()

    def test_returns_value(self):
        value = 'test'
        fake_peekorator = Mock()
        fake_peekorator.__peek__ = Mock()
        fake_peekorator.__peek__.return_value = value
        result = peek(fake_peekorator)
        self.assertEqual(result, value)

    def test_throws_stop_iteration(self):
        fake_peekorator = Mock()
        fake_peekorator.__peek__ = self.throwing_peekorator
        with self.assertRaises(StopIteration):
            peek(fake_peekorator)

    def test_returns_default(self):
        fake_peekorator = Mock()
        fake_peekorator.__peek__ = self.throwing_peekorator
        default_value = 'test'
        result = peek(fake_peekorator, default=default_value)
        self.assertEqual(result, default_value)


class TestPeekorator(TestCase):

    def test_sequential_use(self):
        peekorator = Peekorator([1, 2, 3])
        self.assertEqual(1, peekorator.peek())
        self.assertEqual(1, peekorator.next())
        self.assertEqual(2, peekorator.peek())
        self.assertEqual(2, peekorator.next())
        self.assertEqual(3, peekorator.peek())
        self.assertEqual(3, peekorator.next())

    def test_stored_used(self):
        peekorator = Peekorator(iter([1, 2, 3]))
        self.assertEqual(1, peekorator.peek())
        self.assertEqual(2, peekorator.peek(1))
        self.assertEqual(3, peekorator.peek(2))

        self.assertEqual(1, peekorator.next())
        self.assertEqual(2, peekorator.next())
        self.assertEqual(3, peekorator.next())

    def test_iteration(self):
        iterations = [0, 1, 2]
        peekorator = Peekorator(iter(iterations))
        for i, value in enumerate(peekorator):
            self.assertEqual(value, iterations[i])

    def test_stored_exception(self):
        peekorator = Peekorator(iter([1, 2, 3]))

        with self.assertRaises(StopIteration):
            peekorator.peek(3)

        self.assertEqual(1, peekorator.next())
        self.assertEqual(2, peekorator.next())
        self.assertEqual(3, peekorator.next())

        with self.assertRaises(StopIteration):
            peekorator.next()

    def test_double_stored_exception(self):
        peekorator = Peekorator(iter([1, 2, 3]))

        with self.assertRaises(StopIteration):
            peekorator.peek(3)

        with self.assertRaises(StopIteration):
            peekorator.peek(3)

    def test_first_last(self):
        peekorator = Peekorator([1, 2, 3])

        self.assertTrue( peekorator.is_first() )
        self.assertFalse( peekorator.is_last() )

        self.assertEqual( 1, next(peekorator) )
        self.assertTrue( peekorator.is_first() )
        self.assertFalse( peekorator.is_last() )

        self.assertEqual( 2, next(peekorator) )
        self.assertFalse( peekorator.is_first() )
        self.assertFalse( peekorator.is_last() )

        self.assertEqual( 3, next(peekorator) )
        self.assertFalse( peekorator.is_first() )
        self.assertTrue( peekorator.is_last() )

    def test_first_last_2(self):
        peekorator = Peekorator([])

        self.assertTrue( peekorator.is_first() )
        self.assertTrue( peekorator.is_last() )

        peekorator = Peekorator([1])

        self.assertTrue( peekorator.is_first() )
        self.assertFalse( peekorator.is_last() )

        self.assertEqual( 1, next(peekorator) )
        self.assertTrue( peekorator.is_first() )
        self.assertTrue( peekorator.is_last() )
