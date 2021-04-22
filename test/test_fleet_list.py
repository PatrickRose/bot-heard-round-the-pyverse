"""
Unit tests for fleet list
"""

import unittest

from bot_heard_round.fleet import FleetList, CombatColumn
from bot_heard_round.ship import Ship, ShipType


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

    def test_from_str(self):
        """
        Test providing a string does the right thing
        """
        fleet_with_one_fighter = FleetList()
        fleet_with_one_fighter.columns[0].add_ship(Ship(10, ShipType.FIGHTER), 0)

        fleet_with_damaged_fighter = FleetList()
        fleet_with_damaged_fighter.columns[0].add_ship(Ship(8, ShipType.FIGHTER), 0)

        fleet_with_fighter_in_each_column = FleetList()
        for column in fleet_with_fighter_in_each_column.columns:
            column.add_ship(Ship(10, ShipType.FIGHTER), 0)

        fleet_with_fighter_and_cruiser_in_each_column = FleetList()
        for column in fleet_with_fighter_and_cruiser_in_each_column.columns:
            column.add_ship(Ship(10, ShipType.FIGHTER), 0)
            column.add_ship(Ship(10, ShipType.CRUISER), 1)

        test_cases = [
            (
                FleetList(),
                ''
            ),
            (
                fleet_with_one_fighter,
                'F10[1,0]'
            ),
            (
                fleet_with_damaged_fighter,
                'F8[1,0]'
            ),
            (
                fleet_with_fighter_in_each_column,
                'F10[1,0]|F10[2,0]|F10[3,0]|F10[4,0]|F10[5,0]'
            ),
            (
                fleet_with_fighter_and_cruiser_in_each_column,
                'F10[1,0]|F10[2,0]|F10[3,0]|F10[4,0]|F10[5,0]|'
                'C10[1,1]|C10[2,1]|C10[3,1]|C10[4,1]|C10[5,1]'
            ),
        ]

        for expected, fleet_string in test_cases:
            with self.subTest(str=fleet_string):
                self.assertEqual(expected, FleetList.from_str(fleet_string))


if __name__ == '__main__':
    unittest.main()
