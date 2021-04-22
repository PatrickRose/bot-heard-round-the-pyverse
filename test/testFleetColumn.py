import unittest
from unittest.mock import MagicMock, create_autospec

from bot_heard_round.Fleet import FleetColumn
from bot_heard_round.Ship import Ship, ShipType


class FleetColumnTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.FleetColumn = FleetColumn(1)

    def test_can_add_ship(self):
        ship_1 = MagicMock()

        self.FleetColumn.add_ship(
            ship=ship_1,
            position=1
        )

        self.assertListEqual([(ship_1, 1)], self.FleetColumn.ships)

    def test_orders_ship_when_adding(self):
        ship_1 = MagicMock()
        ship_2 = MagicMock()

        self.FleetColumn.add_ship(
            ship=ship_2,
            position=2
        )

        self.FleetColumn.add_ship(
            ship=ship_1,
            position=1
        )

        self.assertListEqual([(ship_1, 1), (ship_2, 2)], self.FleetColumn.ships)

    def test_can_be_stringified(self):
        ship_1 = create_autospec(Ship)
        ship_1.__str__.return_value = 'SHIP_1'
        ship_2 = create_autospec(Ship)
        ship_2.__str__.return_value = 'SHIP_2'

        self.FleetColumn.add_ship(
            ship=ship_2,
            position=2
        )

        self.FleetColumn.add_ship(
            ship=ship_1,
            position=1
        )

        self.assertEqual(
            'Fleet column 1\nShips: `SHIP_1`, `SHIP_2`',
            str(self.FleetColumn)
        )

    def test_can_create_from_string(self):
        fighter = Ship(10, ShipType.FIGHTER)
        cruiser = Ship(10, ShipType.CRUISER)

        test_cases = [
            (FleetColumn(1), 'Fleet column 1'),
            (FleetColumn(2), 'Fleet column 2'),
            (FleetColumn(1, ships=[(cruiser, 0)]), f'Fleet column 1\nShips: `{cruiser}`'),
            (FleetColumn(1, ships=[(cruiser, 0),(fighter, 1)]), f'Fleet column 1\nShips: `{cruiser}`, `{fighter}`')
        ]

        for expected, string in test_cases:
            with self.subTest(str=string):
                actual = FleetColumn.from_string(string)
                self.assertEqual(expected, actual, f'"{str(expected)}" != "{str(actual)}"')
            with self.subTest('String representation matches', fleet_column=expected):
                actual = FleetColumn.from_string(str(expected))
                self.assertEqual(expected, actual, f'"{str(expected)}" != "{str(actual)}"')

    def test_equality(self):
        fighter = Ship(10, ShipType.FIGHTER)
        cruiser = Ship(10, ShipType.CRUISER)

        damaged_fighter = Ship(3, ShipType.FIGHTER)
        damaged_cruiser = Ship(3, ShipType.CRUISER)

        test_cases = [
            (FleetColumn(1), FleetColumn(1), True),
            (FleetColumn(2), FleetColumn(1), False),
            (FleetColumn(1), FleetColumn(1, ships=[(fighter, 0)]), False),
            (FleetColumn(1, ships=[(fighter, 0)]), FleetColumn(1, ships=[(fighter, 0)]), True),
            (FleetColumn(1, ships=[(fighter, 0)]), FleetColumn(1, ships=[(cruiser, 0)]), False),
            (FleetColumn(1, ships=[(fighter, 0)]), FleetColumn(1, ships=[(damaged_fighter, 0)]), False),
            (FleetColumn(1, ships=[(fighter, 0), (damaged_cruiser, 1)]), FleetColumn(1, ships=[(damaged_cruiser, 0), (fighter, 1)]), False),
            (FleetColumn(1, ships=[(fighter, 0), (damaged_cruiser, 1)]), FleetColumn(1, ships=[(fighter, 0), (damaged_cruiser, 1)]), True),
        ]

        for first, second, result in test_cases:
            with self.subTest(first=first, second=second):
                self.assertEqual(result, first == second)
            with self.subTest(first=second, second=first):
                self.assertEqual(result, second == first)


if __name__ == '__main__':
    unittest.main()
