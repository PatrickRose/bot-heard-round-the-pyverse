"""
Unit tests for fleet column
"""

import unittest
from unittest.mock import MagicMock, create_autospec

from bot_heard_round.fleet import FleetColumn
from bot_heard_round.ship import Ship, ShipType


class FleetColumnTestCase(unittest.TestCase):
    """
    Tests for fleet column
    """

    def setUp(self) -> None:
        """
        Set up an empty fleet column
        """
        self.fleet_column = FleetColumn(1)

    def test_can_add_ship(self):
        """
        Test that we can add a chip
        """
        ship_1 = MagicMock()

        self.fleet_column.add_ship(
            ship=ship_1,
            position=1
        )

        self.assertListEqual([(ship_1, 1)], self.fleet_column.ships)

    def test_orders_ship_when_adding(self):
        """
        Test that ships are ordered when added
        """
        ship_1 = MagicMock()
        ship_2 = MagicMock()

        self.fleet_column.add_ship(
            ship=ship_2,
            position=2
        )

        self.fleet_column.add_ship(
            ship=ship_1,
            position=1
        )

        self.assertListEqual([(ship_1, 1), (ship_2, 2)], self.fleet_column.ships)

    def test_can_be_stringified(self):
        """
        Test that we can stringify a fleet column
        """
        ship_1 = create_autospec(Ship)
        ship_1.__str__.return_value = 'SHIP_1'
        ship_2 = create_autospec(Ship)
        ship_2.__str__.return_value = 'SHIP_2'

        self.fleet_column.add_ship(
            ship=ship_2,
            position=2
        )

        self.fleet_column.add_ship(
            ship=ship_1,
            position=1
        )

        self.assertEqual(
            'Fleet column 1\nShips: `SHIP_1`, `SHIP_2`',
            str(self.fleet_column)
        )

    def test_can_create_from_string(self):
        """
        Test we can create a fleet from a string
        """
        frigate = Ship(10, ShipType.FRIGATE)
        cruiser = Ship(10, ShipType.LIGHT_CRUISER)

        test_cases = [
            (FleetColumn(1), 'Fleet column 1'),
            (FleetColumn(2), 'Fleet column 2'),
            (
                FleetColumn(1, ships=[(cruiser, 0)]),
                f'Fleet column 1\nShips: `{cruiser}`'
            ),
            (
                FleetColumn(1, ships=[(cruiser, 0), (frigate, 1)]),
                f'Fleet column 1\nShips: `{cruiser}`, `{frigate}`'
            )
        ]

        for expected, string in test_cases:
            with self.subTest(str=string):
                actual = FleetColumn.from_string(string)
                self.assertEqual(expected, actual, f'"{str(expected)}" != "{str(actual)}"')
            with self.subTest('String representation matches', fleet_column=expected):
                actual = FleetColumn.from_string(str(expected))
                self.assertEqual(expected, actual, f'"{str(expected)}" != "{str(actual)}"')

    def test_equality(self):
        """
        Test equality method
        """
        fighter = Ship(10, ShipType.FRIGATE)
        cruiser = Ship(10, ShipType.LIGHT_CRUISER)

        damaged_fighter = Ship(3, ShipType.FRIGATE)
        damaged_cruiser = Ship(3, ShipType.LIGHT_CRUISER)

        test_cases = [
            (
                FleetColumn(1),
                FleetColumn(1),
                True
            ),
            (
                FleetColumn(2),
                FleetColumn(1),
                False
            ),
            (
                FleetColumn(1),
                FleetColumn(1, ships=[(fighter, 0)]),
                False
            ),
            (
                FleetColumn(1, ships=[(fighter, 0)]),
                FleetColumn(1, ships=[(fighter, 0)]),
                True
            ),
            (
                FleetColumn(1, ships=[(fighter, 0)]),
                FleetColumn(1, ships=[(cruiser, 0)]),
                False
            ),
            (
                FleetColumn(1, ships=[(fighter, 0)]),
                FleetColumn(1, ships=[(damaged_fighter, 0)]),
                False
            ),
            (
                FleetColumn(1, ships=[(fighter, 0), (damaged_cruiser, 1)]),
                FleetColumn(1, ships=[(damaged_cruiser, 0), (fighter, 1)]),
                False
            ),
            (
                FleetColumn(1, ships=[(fighter, 0), (damaged_cruiser, 1)]),
                FleetColumn(1, ships=[(fighter, 0), (damaged_cruiser, 1)]),
                True
            ),
        ]

        for first, second, result in test_cases:
            with self.subTest(first=first, second=second):
                self.assertEqual(result, first == second)
            with self.subTest(first=second, second=first):
                self.assertEqual(result, second == first)

    def test_taking_damage(self):
        test_cases = [
            (
                FleetColumn(-1, ships=[(Ship(10, ShipType.FRIGATE), 0)]),
                5,
                FleetColumn(-1, ships=[(Ship(5, ShipType.FRIGATE), 0)]),
                0
            ),
            (
                FleetColumn(-1, ships=[(Ship(10, ShipType.FRIGATE), 0)]),
                10,
                FleetColumn(-1, ships=[]),
                0
            ),
            (
                FleetColumn(-1, ships=[(Ship(10, ShipType.FRIGATE), 0)]),
                15,
                FleetColumn(-1, ships=[]),
                5
            ),
            (
                FleetColumn(-1, ships=[(Ship(10, ShipType.FRIGATE), 0), (Ship(10, ShipType.FRIGATE), 1)]),
                15,
                FleetColumn(-1, ships=[(Ship(5, ShipType.FRIGATE), 1)]),
                0
            ),
        ]

        for base, damage, expected, carry_over in test_cases:
            with self.subTest():
                actual_carry, _ = base.take_damage(damage)
                self.assertEqual(base, expected)
                self.assertEqual(carry_over, actual_carry)


if __name__ == '__main__':
    unittest.main()
