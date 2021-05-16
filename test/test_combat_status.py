"""
Test combat status
"""
import unittest

from bot_heard_round.combat_status import CombatStatus, CombatRound
from bot_heard_round.fleet import FleetList, FleetColumn, CombatColumn
from bot_heard_round.ship import Ship, ShipType


class TestCombatStatus(unittest.TestCase):
    def test_combat_round_applies_damage(self):
        combat = CombatStatus(
            (
                None,
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            (
                None,
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            CombatRound.MISSILE_ONE
        )

        message = combat.resolve_combat_round()

        expected_fleet = FleetList((FleetColumn(1, CombatColumn.RIGHT, ships=[(Ship(6, ShipType.LIGHT_CRUISER), 0),
                                                                              (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(2, CombatColumn.MIDDLE, ships=[(Ship(6, ShipType.LIGHT_CRUISER), 0),
                                                                               (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(3, CombatColumn.LEFT, ships=[(Ship(6, ShipType.LIGHT_CRUISER), 0),
                                                                             (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(4, CombatColumn.WAITING, ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                                                (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(5, CombatColumn.WAITING, ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                                                (
                                                                                    Ship(10, ShipType.LIGHT_CRUISER),
                                                                                    0)]),)
                                   )
        self.assertEqual(
            combat.attacker_fleet,
            expected_fleet,
            "Did not match, combat messages were\n{}".format('\n'.join(message))
        )

        self.assertEqual(
            combat.defender_fleet,
            expected_fleet,
            "Did not match, combat messages were\n{}".format('\n'.join(message))
        )

    def test_railgun_combat_round_has_no_defence(self):
        combat = CombatStatus(
            (
                None,
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            (
                None,
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0), (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            CombatRound.RAIL_GUN
        )

        message = combat.resolve_combat_round()

        expected_fleet = FleetList((FleetColumn(1, CombatColumn.RIGHT, ships=[]),
                                    FleetColumn(2, CombatColumn.MIDDLE, ships=[]),
                                    FleetColumn(3, CombatColumn.LEFT, ships=[]),
                                    FleetColumn(4, CombatColumn.WAITING, ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                                                (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(5, CombatColumn.WAITING, ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                                                (
                                                                                    Ship(10, ShipType.LIGHT_CRUISER),
                                                                                    0)]),)
                                   )
        self.assertEqual(
            combat.attacker_fleet,
            expected_fleet,
            "Did not match, combat messages were\n{}".format('\n'.join(message))
        )

        self.assertEqual(
            combat.defender_fleet,
            expected_fleet,
            "Did not match, combat messages were\n{}".format('\n'.join(message))
        )


if __name__ == '__main__':
    unittest.main()
