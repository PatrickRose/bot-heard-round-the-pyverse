"""
Unit tests for fleet list
"""
import unittest

from bot_heard_round import emoji
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
        fleet_with_one_frigate = FleetList()
        fleet_with_one_frigate.columns[0].add_ship(Ship(10, ShipType.FRIGATE), 0)

        fleet_with_damaged_frigate = FleetList()
        fleet_with_damaged_frigate.columns[0].add_ship(Ship(8, ShipType.FRIGATE), 0)

        fleet_with_frigate_in_each_column = FleetList()
        for column in fleet_with_frigate_in_each_column.columns:
            column.add_ship(Ship(10, ShipType.FRIGATE), 0)

        fleet_with_frigate_and_cruiser_in_each_column = FleetList()
        for column in fleet_with_frigate_and_cruiser_in_each_column.columns:
            column.add_ship(Ship(10, ShipType.FRIGATE), 0)
            column.add_ship(Ship(10, ShipType.LIGHT_CRUISER), 1)

        frigate_char = ShipType.FRIGATE.to_char()
        cruiser_char = ShipType.LIGHT_CRUISER.to_char()
        test_cases = [
            (
                FleetList(),
                ''
            ),
            (
                fleet_with_one_frigate,
                f'{frigate_char}10[1,0]'
            ),
            (
                fleet_with_damaged_frigate,
                f'{frigate_char}8[1,0]'
            ),
            (
                fleet_with_frigate_in_each_column,
                f'{frigate_char}10[1,0]|{frigate_char}10[2,0]|'
                f'{frigate_char}10[3,0]|{frigate_char}10[4,0]|'
                f'{frigate_char}10[5,0]'
            ),
            (
                fleet_with_frigate_and_cruiser_in_each_column,
                f'{frigate_char}10[1,0]|{frigate_char}10[2,0]|'
                f'{frigate_char}10[3,0]|{frigate_char}10[4,0]|'
                f'{frigate_char}10[5,0]|{cruiser_char}10[1,1]|'
                f'{cruiser_char}10[2,1]|{cruiser_char}10[3,1]|'
                f'{cruiser_char}10[4,1]|{cruiser_char}10[5,1]'
            ),
        ]

        for expected, fleet_string in test_cases:
            with self.subTest(str=fleet_string):
                actual = FleetList.from_str(fleet_string)
                self.assertEqual(expected, actual, '{} did not match {}'.format(expected, actual))

            with self.subTest('Patrol mode', str='<P>' + fleet_string):
                expected.patrol_mode = True
                actual = FleetList.from_str('<P>' + fleet_string)
                self.assertEqual(expected, actual, '{} did not match {}'.format(expected, actual))

    def test_can_handle_all_fleet_strs(self):
        """
        Test every ship type can be handled in a fleet string
        :return:
        """
        for member in ShipType:
            base_ship = f'{member.to_char()}10'

            with self.subTest(ship_type=member):
                expected = FleetList()
                expected.columns[0].add_ship(Ship(10, member), 0)

                self.assertEqual(expected, FleetList.from_str(f'{base_ship}[1,0]'))
            with self.subTest('Two ships, same column', ship_type=member):
                expected = FleetList()
                expected.columns[0].add_ship(Ship(10, member), 0)
                expected.columns[0].add_ship(Ship(10, member), 1)
                self.assertEqual(expected, FleetList.from_str(f'{base_ship}[1,0]|{base_ship}[1,1]'))

    def test_can_ask_for_options_for_fleet_swap(self):
        """
        Test fleet swap
        :return:
        """
        fleet_list = FleetList()
        selected_column = {
            1: CombatColumn.LEFT,
            2: CombatColumn.MIDDLE,
            3: CombatColumn.RIGHT,
            4: CombatColumn.WAITING,
            5: CombatColumn.WAITING,
        }

        for column in fleet_list.columns:
            column.add_ship(Ship(10, ShipType.FRIGATE), 0)
            column.combat_column = selected_column[column.column_number]

        expected = (
            {
                emoji.CROSS_EMOJI: None,
                emoji.LEFT_EMOJI: 1,
                emoji.CENTRE_EMOJI: 2,
                emoji.RIGHT_EMOJI: 3,
            },
            {
                emoji.FOUR_EMOJI: 4,
                emoji.FIVE_EMOJI: 5
            }
        )

        self.assertEqual(
            expected,
            fleet_list.swap_options()
        )

    def test_asking_for_options_with_no_waiting_fleets_triggers_error(self):
        """
        Test fleet swap
        :return:
        """
        fleet_list = FleetList()

        self.assertRaises(
            FleetList.NoWaitingFleetError,
            fleet_list.swap_options
        )


if __name__ == '__main__':
    unittest.main()
