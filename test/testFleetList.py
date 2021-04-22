import unittest

from bot_heard_round.CombatColumn import CombatColumn
from bot_heard_round.Fleet import FleetList


class FleetListTest(unittest.TestCase):
    def test_base_columns_are_all_waiting(self):
        fleet = FleetList()
        self.assertListEqual(list(fleet.columns), fleet.where_column(CombatColumn.WAITING))

    def test_only_returns_waiting_columns(self):
        fleet = FleetList()

        columns = list(fleet.columns)[1:]
        fleet.columns[0].combat_column = CombatColumn.MIDDLE

        self.assertListEqual(columns, fleet.where_column(CombatColumn.WAITING))

if __name__ == '__main__':
    unittest.main()
