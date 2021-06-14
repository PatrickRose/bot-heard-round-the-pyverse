"""
Test combat status
"""
import unittest
from unittest.mock import MagicMock

from bot_heard_round.combat_status import CombatStatus, CombatRound
from bot_heard_round.fleet import FleetList, FleetColumn, CombatColumn
from bot_heard_round.ship import Ship, ShipType


class TestCombatStatus(unittest.TestCase):
    """
    Tests for the combat status
    """

    def test_combat_round_applies_damage(self):
        """

        :return:
        """
        combat = CombatStatus(
            (
                MagicMock(),
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                ))
            ),
            (
                MagicMock(),
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                ))
            ),
            CombatRound.MISSILE_ONE
        )

        message = combat.resolve_combat_round()

        expected_fleet = FleetList((FleetColumn(1,
                                                CombatColumn.RIGHT,
                                                ships=[(Ship(6, ShipType.LIGHT_CRUISER), 0),
                                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(2,
                                                CombatColumn.MIDDLE,
                                                ships=[(Ship(6, ShipType.LIGHT_CRUISER), 0),
                                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(3,
                                                CombatColumn.LEFT,
                                                ships=[(Ship(6, ShipType.LIGHT_CRUISER), 0),
                                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(4,
                                                CombatColumn.WAITING,
                                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(5,
                                                CombatColumn.WAITING,
                                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),)
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
        """
        :return:
        """
        combat = CombatStatus(
            (
                MagicMock(),
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0),
                                    (Ship(10, ShipType.LIGHT_CRUISER), 0)
                                ]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            (
                MagicMock(),
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            CombatRound.RAIL_GUN
        )

        message = combat.resolve_combat_round()

        expected_fleet = FleetList((FleetColumn(1, CombatColumn.RIGHT, ships=[]),
                                    FleetColumn(2, CombatColumn.MIDDLE, ships=[]),
                                    FleetColumn(3, CombatColumn.LEFT, ships=[]),
                                    FleetColumn(4,
                                                CombatColumn.WAITING,
                                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                                    FleetColumn(5,
                                                CombatColumn.WAITING,
                                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),)
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

    def test_applies_rollover_damage_to_adjacent_fleets(self):
        """
        :return:
        """
        combat = CombatStatus(
            (
                MagicMock(),
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(100, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(2, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            (
                MagicMock(),
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(100, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(1, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(1, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            CombatRound.MISSILE_ONE
        )

        message = combat.resolve_combat_round()

        expected_attacker_fleet = FleetList(
            (FleetColumn(1, CombatColumn.RIGHT, ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0)]),
             FleetColumn(2, CombatColumn.MIDDLE, ships=[(Ship(98, ShipType.LIGHT_CRUISER), 0)]),
             FleetColumn(3, CombatColumn.LEFT, ships=[]),
             FleetColumn(4, CombatColumn.WAITING, ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                         (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
             FleetColumn(5, CombatColumn.WAITING, ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                                         (Ship(10, ShipType.LIGHT_CRUISER), 0)]),)
        )
        self.assertEqual(
            combat.attacker_fleet,
            expected_attacker_fleet,
            "Attacker {} did not match {}, combat messages were\n{}".format(
                combat.attacker_fleet,
                expected_attacker_fleet, '\n'.join(message))
        )

        expected_defender_fleet = FleetList((
            FleetColumn(1, CombatColumn.RIGHT,
                        ships=[]),
            FleetColumn(2, CombatColumn.MIDDLE,
                        ships=[(Ship(87, ShipType.LIGHT_CRUISER), 0)]),
            FleetColumn(3, CombatColumn.LEFT,
                        ships=[]),
            FleetColumn(4, CombatColumn.WAITING,
                        ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0),
                               (Ship(1, ShipType.LIGHT_CRUISER), 0)]),
            FleetColumn(5, CombatColumn.WAITING,
                        ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0),
                               (Ship(1, ShipType.LIGHT_CRUISER), 0)]),
        ))

        self.assertEqual(
            combat.defender_fleet,
            expected_defender_fleet,
            "Defender {} did not match {}, combat messages were\n{}".format(
                combat.defender_fleet,
                expected_defender_fleet, '\n'.join(message))
        )

    def test_string_representation(self):
        """

        :return:
        """
        attacker = MagicMock()
        attacker.display_name = 'ATTACKER'

        defender = MagicMock()
        defender.display_name = 'DEFENDER'

        combat_status = CombatStatus(
            (
                attacker,
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(2, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(3, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(10, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(10, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            (
                defender,
                FleetList((
                    FleetColumn(1, CombatColumn.RIGHT,
                                ships=[]),
                    FleetColumn(2, CombatColumn.MIDDLE,
                                ships=[(Ship(2, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(3, CombatColumn.LEFT,
                                ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(4, CombatColumn.WAITING,
                                ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(1, ShipType.LIGHT_CRUISER), 0)]),
                    FleetColumn(5, CombatColumn.WAITING,
                                ships=[(Ship(1, ShipType.LIGHT_CRUISER), 0),
                                       (Ship(1, ShipType.LIGHT_CRUISER), 0)]),
                ))
            ),
            CombatRound.MISSILE_ONE
        )

        self.assertEqual(
            """`!!! Combat status - round 1 !!!`
Attacker: `ATTACKER`
Defender: `DEFENDER`
Attacker ships in reserve:
Fleet column 4
Ships: `Light Cruiser (10/15)`, `Light Cruiser (10/15)`
Fleet column 5
Ships: `Light Cruiser (10/15)`, `Light Cruiser (10/15)`
Defender ships reserve:
Fleet column 4
Ships: `Light Cruiser (1/15)`, `Light Cruiser (1/15)`
Fleet column 5
Ships: `Light Cruiser (1/15)`, `Light Cruiser (1/15)`
```
|         Left         |        Middle        |        Right         |
|----------------------|----------------------|----------------------|
| Light Cruiser (3/15) | Light Cruiser (2/15) | Light Cruiser (1/15) |
|        -----         |        -----         |        -----         |
| Light Cruiser (1/15) | Light Cruiser (2/15) |                      |
```""",
            str(combat_status)
        )


if __name__ == '__main__':
    unittest.main()
