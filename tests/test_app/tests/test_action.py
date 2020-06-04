import datetime
from typing import Optional

from logux.core import ActionCommand, Meta, Action
from tests.test_app.tests.helpers import LoguxTestCase


class LoguxActionCommandTestCase(LoguxTestCase):
    def test_property_getters(self):
        """ Tests for Action helpers """

        class TestActionCommand(ActionCommand):

            def access(self, a: Action, m: Optional[Meta]) -> bool:
                return True

        action = TestActionCommand([
            'action',
            {'type': 'user/rename', 'user': 38, 'name': 'New'},
            {'id': "1560954012838 38:Y7bysd:O0ETfc 0", 'time': 1560954012838}
        ])

        self.assertEqual(action.meta.user_id, '38')
        self.assertEqual(action.meta.client_id, '38:Y7bysd')
        self.assertEqual(action.meta.node_id, 'O0ETfc')
        self.assertEqual(action.meta.time, datetime.fromtimestamp(1560954012838 / 1e3))

        action_without_node_id = TestActionCommand([
            'action',
            {'type': 'user/rename', 'user': 38, 'name': 'New'},
            {'id': "1560954012838 38:Y7bysd 0", 'time': 1560954012838}
        ])
        self.assertIsNone(action_without_node_id._meta.node_id)

    def test_meta_cmp(self):
        """ Tests for meta compering """

        # time of m2 gt
        m1 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': '1560954012838'})  # '2019-06-20 00:20:12.838000'
        m2 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 1', 'time': '1560954012848'})  # '2019-06-20 00:20:12.848000'

        self.assertTrue(m1 < m2)
        self.assertTrue(m1 != m2)
        self.assertFalse(m1 > m2)
        self.assertFalse(m1 == m2)

        # times is eq, but counter m2 is gt
        m1 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': '1560954012838'})
        m2 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 1', 'time': '1560954012838'})

        self.assertTrue(m1 < m2)
        self.assertTrue(m1 != m2)
        self.assertFalse(m1 > m2)
        self.assertFalse(m1 == m2)

        # times is eq, counters is eq, but client_id m2 is gt
        m1 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': '1560954012838'})
        m2 = Meta({'id': '1560954012838 38:Z7bysd:O0ETfc 0', 'time': '1560954012838'})

        self.assertTrue(m1 < m2)
        self.assertTrue(m1 != m2)
        self.assertFalse(m1 > m2)
        self.assertFalse(m1 == m2)

        # m1 and m2 – compactly eq
        m1 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': '1560954012838'})
        m2 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': '1560954012838'})

        self.assertFalse(m1 < m2)
        self.assertFalse(m1 != m2)
        self.assertFalse(m1 > m2)
        self.assertTrue(m1 == m2)
