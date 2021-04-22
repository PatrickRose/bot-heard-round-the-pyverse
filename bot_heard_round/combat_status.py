"""
Module holding the combat status content
"""

import enum
import re
from typing import Optional

import discord
from discord import WidgetMember

from bot_heard_round.fleet import FleetList, CombatColumn
from bot_heard_round.utils import get_user_from_nick_or_name

attack_defend_regex = re.compile('(Attacker|Defender): `(.+)`')
round_regex = re.compile('`!!! Combat status( - round (\\d)| - finished)? !!!`')
ship_regex = re.compile('`(.+?) \\((\\w+) (\\d+)/(\\d+)\\)`')

UserAndFleet = tuple[discord.WidgetMember, FleetList]


class CombatRound(enum.Enum):
    """
    Enum for the different combat rounds
    """
    PENDING = 0
    MISSILE_ONE = 1
    MISSILE_TWO = 2
    RAIL_GUN = 3
    FINISHED = 4


class CombatStatus:
    """
    Encapsulates the combat status for the current combat
    """
    attacker: WidgetMember
    attacker_fleet: FleetList
    defender: WidgetMember
    defender_fleet: FleetList

    def __init__(self,
                 attacker,
                 defender,
                 combat_round: CombatRound = CombatRound.PENDING):
        if not isinstance(attacker, tuple):
            attacker = (attacker, FleetList())
        if not isinstance(defender, tuple):
            defender = (defender, FleetList())

        self.attacker = attacker[0]
        self.defender = defender[0]
        self.attacker_fleet = attacker[1]
        self.defender_fleet = defender[1]
        self.combat_round = combat_round

    def add_fleet_for(self, user: discord.WidgetMember, fleet: str):
        """

        :param user:
        :param fleet:
        """
        if user.id == self.attacker.id:
            self.attacker_fleet = FleetList.from_str(fleet)
        else:
            self.defender_fleet = FleetList.from_str(fleet)

    def __str__(self):
        attacker = self.attacker.display_name
        defender = self.defender.display_name

        attacker_fleet_waiting = self.attacker_fleet.where_column(CombatColumn.WAITING)

        defender_fleet_waiting = self.defender_fleet.where_column(CombatColumn.WAITING)

        attacker_fleet_waiting.sort(
            key=lambda x: x.column_number
        )

        defender_fleet_waiting.sort(
            key=lambda x: x.column_number
        )

        if self.combat_round == CombatRound.PENDING:
            status = "`!!! Combat status !!!`"
        elif self.combat_round == CombatRound.MISSILE_ONE:
            status = "`!!! Combat status - round 1 !!!`"
        elif self.combat_round == CombatRound.MISSILE_TWO:
            status = "`!!! Combat status - round 2 !!!`"
        elif self.combat_round == CombatRound.RAIL_GUN:
            status = "`!!! Combat status - round 3 !!!`"
        else:
            status = "`!!! Combat status - finished !!!`"

        rows = [
            status,
            "Attacker: `{}`".format(attacker),
            "Defender: `{}`".format(defender)
        ]

        if attacker_fleet_waiting:
            rows.append(
                "Attacker ships to apply:\n{}".format(
                    '\n'.join(['{}'.format(str(x)) for x in attacker_fleet_waiting])
                )
            )

        if defender_fleet_waiting:
            rows.append(
                "Defender ships to apply:\n{}".format(
                    '\n'.join(['{}'.format(str(x)) for x in defender_fleet_waiting])
                )
            )

        attacker_fleet_ready = self.attacker_fleet.where_column(CombatColumn.MIDDLE)
        defender_fleet_ready = self.defender_fleet.where_column(CombatColumn.MIDDLE)

        if attacker_fleet_ready or defender_fleet_ready:
            attacker_fleet_ready.sort(key=lambda x: x[1].position, reverse=True)
            defender_fleet_ready.sort(key=lambda x: x[1].position)

            # rows.append(
            #     '```\n' + tabulate.tabulate(
            #         [str(x[0]) for x in attacker_fleet_ready] +
            #         ['------'] +
            #         [str(x[0]) for x in defender_fleet_ready]
            #     ) + '\n```'
            # )

        return "\n".join(rows)

    def ready_for_combat(self):
        """

        :rtype: bool
        """
        attacker = False
        defender = False

        for column in self.attacker_fleet.columns:
            if column.ships:
                attacker = True
                break

        for column in self.defender_fleet.columns:
            if column.ships:
                defender = True
                break

        return attacker and defender

    @classmethod
    async def from_message(cls, message: discord.Message):
        """

        :param message:
        :return:
        """
        content = message.content
        attacker: Optional[discord.User] = None
        defender: Optional[discord.User] = None
        combat_round = None
        defender_ships = FleetList()
        attacker_ships = FleetList()

        members = await message.guild.fetch_members().flatten()

        for line in content.split("\n"):
            match = round_regex.match(line)
            if match:
                combat_round = cls.make_combat_round(match)

            match = attack_defend_regex.match(line)

            if match:
                attack_defend = match.group(1)
                user = get_user_from_nick_or_name(match.group(2), members)

                if not user:
                    raise ValueError(
                        'Could not find user with name/nickname {}'.format(match.group(2))
                    )

                if attack_defend == 'Attacker':
                    attacker = user
                else:
                    defender = user

        if not attacker or not defender:
            raise ValueError('Missing an attacker or defender in the pinned message?')

        return CombatStatus(
            (attacker, attacker_ships),
            (defender, defender_ships),
            combat_round=combat_round
        )

    @classmethod
    def make_combat_round(cls, match: re) -> CombatRound:
        """

        :param match:
        :return:
        """
        if match.group(2) is None:
            combat_round = CombatRound.PENDING \
                if match.group(1) is None \
                else CombatRound.FINISHED
        else:
            combat_round = [
                'EMPTY',
                CombatRound.MISSILE_ONE,
                CombatRound.MISSILE_TWO,
                CombatRound.RAIL_GUN
            ][int(match.group(2))]
        return combat_round
