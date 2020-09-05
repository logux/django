from django.test import TestCase

from logux.core import Meta


class MetaTestCase(TestCase):
    """ Tests for meta arithmetic. """

    def test_entries_by_time(self):
        a = Meta({'id': '2 a 0', 'time': 2})
        b = Meta({'id': '1 a 0', 'time': 1})

        self.assertFalse(a.is_older(b))
        self.assertTrue(b.is_older(a))

        self.assertFalse(a > b)
        self.assertTrue(a < b)

    def test_entries_by_real_time(self):
        a = Meta({'id': '1 a 0', 'time': 2})
        b = Meta({'id': '1 a 0', 'time': 1})

        self.assertFalse(a.is_older(b))
        self.assertTrue(b.is_older(a))

        self.assertFalse(a > b)
        self.assertTrue(a < b)

    def test_entries_by_other_ID_parts(self):
        a = Meta({'id': '1 a 9', 'time': 1})
        b = Meta({'id': '1 a 10', 'time': 1})

        self.assertTrue(a.is_older(b))
        self.assertFalse(b.is_older(a))

        self.assertTrue(a > b)
        self.assertFalse(a < b)

    def test_entries_by_other_ID_parts_with_priority(self):
        a = Meta({'id': '1 b 1', 'time': 1})
        b = Meta({'id': '1 a 1', 'time': 1})

        self.assertFalse(a.is_older(b))
        self.assertTrue(b.is_older(a))

        self.assertFalse(a > b)
        self.assertTrue(a < b)

    def test_entries_with_same_time(self):
        a = Meta({'id': '2 a 0', 'time': 1})
        b = Meta({'id': '1 a 0', 'time': 1})

        self.assertFalse(a.is_older(b))
        self.assertTrue(b.is_older(a))

        self.assertFalse(a > b)
        self.assertTrue(a < b)

    def test_returns_false_for_same_entry(self):
        a = Meta({'id': '1 b 1', 'time': 1})

        self.assertFalse(a.is_older(a))

        self.assertFalse(a > a)
        self.assertFalse(a < a)

    def test_orders_entries_with_different_node_ID_length(self):
        a = Meta({'id': '1 11 1', 'time': 1})
        b = Meta({'id': '1 1 2', 'time': 1})

        self.assertFalse(a.is_older(b))
        self.assertTrue(b.is_older(a))

        self.assertFalse(a > b)
        self.assertTrue(a < b)

    def test_works_with_undefined_in_one_meta(self):
        a = Meta({'id': '1 a 0', 'time': 1})

        self.assertFalse(a.is_older(None))
