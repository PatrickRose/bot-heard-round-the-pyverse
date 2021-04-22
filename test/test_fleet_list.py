"""
Unit tests for fleet list
"""

import unittest

from bot_heard_round.fleet import FleetList, CombatColumn


class FleetListTest(unittest.TestCase):
    """
    Tests for fleet list
    """

    def test_base_columns_are_all_waiting(self):
        """
        Test that where_column returns all columns
        :return:
        """
        fleet = FleetList()
        self.assertListEqual(list(fleet.columns), fleet.where_column(CombatColumn.WAITING))

    def test_only_returns_waiting_columns(self):
        """
        Test that where_column returns the right columns
        :return:
        """
        fleet = FleetList()

        columns = list(fleet.columns)[1:]
        fleet.columns[0].combat_column = CombatColumn.MIDDLE

        self.assertListEqual(columns, fleet.where_column(CombatColumn.WAITING))

if __name__ == '__main__':
    unittest.main()
