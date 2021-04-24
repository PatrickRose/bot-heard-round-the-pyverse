"""
Unit tests for the Ship class
"""

import unittest
from unittest.mock import MagicMock, PropertyMock

from bot_heard_round.ship import ShipType, Ship


class TestShip(unittest.TestCase):
    """
    Unit tests for the ship class
    """
    def test_can_convert_to_str_and_back(self):
        """
        Test that we can convert a ship to string and back
        :return:
        """
        ship_type: ShipType
        for ship_type in ShipType:
            for i in range(1, ship_type.max_health+1):
                with self.subTest(shipType=ship_type, health=i):
                    expected = Ship(current_health=i, ship_type=ship_type)
                    self.assertEqual(
                        expected,
                        Ship.from_str(str(expected))
                    )

    def test_proxies_to_ship_type(self):
        """
        Test that we proxy the properties to the ship type
        :return:
        """
        props = ['max_health', 'attack', 'defence']
        for prop in props:
            with self.subTest(prop=prop):
                proxy = MagicMock(ShipType)
                property_mock = PropertyMock(return_value='MOCKED_VALUE')
                setattr(type(proxy), prop, property_mock)
                expected = Ship(1, proxy)

                self.assertEqual(getattr(expected, prop), 'MOCKED_VALUE')

                property_mock.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
