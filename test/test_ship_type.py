"""
Unit test for ship types
"""
import unittest

from bot_heard_round.ship import ShipType, SHIP_MAX_HEALTHS, SHIP_DEFENCES, SHIP_ATTACKS


class TestShipType(unittest.TestCase):
    """
    Unit tests for ship type
    """
    def test_can_be_created_from_string(self):
        """
        Test we can convert it to and back from a string
        :return:
        """
        member: ShipType
        for member in ShipType:
            with self.subTest(ship_type=member):
                self.assertEqual(member, ShipType.from_str(str(member)))

    def test_can_be_created_from_char(self):
        """
        Test we can convert it to and back from a "char"
        :return:
        """
        member: ShipType
        for member in ShipType:
            with self.subTest(ship_type=member):
                self.assertEqual(member, ShipType.from_char(member.to_char()))

    def test_has_max_health(self):
        """
        Test each ship has a max health
        :return:
        """
        member: ShipType
        for member in ShipType:
            with self.subTest(ship_type=member):
                self.assertEqual(SHIP_MAX_HEALTHS[member], member.max_health)

    def test_has_attack(self):
        """
        Test each ship has an attack value
        :return:
        """
        for member in ShipType:
            with self.subTest(ship_type=member):
                self.assertEqual(SHIP_ATTACKS[member], member.attack)

    def test_has_defence(self):
        """
        Test each ship has a defence value
        :return:
        """
        for member in ShipType:
            with self.subTest(ship_type=member):
                self.assertEqual(SHIP_DEFENCES[member], member.defence)


if __name__ == '__main__':
    unittest.main()
