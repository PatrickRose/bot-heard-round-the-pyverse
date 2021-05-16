"""
Module holding the combat status content
"""

import enum
import re
from typing import Optional

import discord
import tabulate
from discord import WidgetMember

from bot_heard_round.fleet import FleetList, CombatColumn, FleetColumn
from bot_heard_round.ship import Ship
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
    message: discord.Message

    def __init__(self,
                 attacker,
                 defender,
                 combat_round: CombatRound = CombatRound.PENDING,
                 message: discord.Message = None):
        if not isinstance(attacker, tuple):
            attacker = (attacker, FleetList())
        if not isinstance(defender, tuple):
            defender = (defender, FleetList())

        self.attacker = attacker[0]
        self.defender = defender[0]
        self.attacker_fleet = attacker[1]
        self.defender_fleet = defender[1]
        self.combat_round = combat_round

        if message:
            self.message = message

    def add_fleet_for(self, for_attacker: bool, fleet: str):
        """

        :param for_attacker:
        :param fleet:
        """
        if for_attacker:
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

        attacker_fleet_activated: dict[CombatColumn, list[tuple[Ship, int]]] = {}
        defender_fleet_activated: dict[CombatColumn, list[tuple[Ship, int]]] = {}

        for column in CombatColumn:
            if column == CombatColumn.WAITING:
                continue

            attacker = self.attacker_fleet.where_column(column)

            if not attacker:
                attacker = FleetColumn(-1)
            else:
                attacker = attacker[0]

            attacker_fleet_activated[column] = attacker.ships

            defender = self.defender_fleet.where_column(column)

            if not defender:
                defender = FleetColumn(-1)
            else:
                defender = defender[0]

            defender_fleet_activated[column] = defender.ships

        ship_table = []

        for i_attacker_pos in range(
                max(len(attacker_fleet_activated[x]) for x in attacker_fleet_activated),
                0,
                -1
        ):
            if i_attacker_pos > len(attacker_fleet_activated[CombatColumn.LEFT]):
                left = ''
            else:
                left = str(attacker_fleet_activated[CombatColumn.LEFT][i_attacker_pos - 1][0])

            if i_attacker_pos > len(attacker_fleet_activated[CombatColumn.MIDDLE]):
                middle = ''
            else:
                middle = str(attacker_fleet_activated[CombatColumn.MIDDLE][i_attacker_pos - 1][0])

            if i_attacker_pos > len(attacker_fleet_activated[CombatColumn.RIGHT]):
                right = ''
            else:
                right = str(attacker_fleet_activated[CombatColumn.RIGHT][i_attacker_pos - 1][0])

            ship_table.append({
                CombatColumn.LEFT: left,
                CombatColumn.MIDDLE: middle,
                CombatColumn.RIGHT: right
            })

            i_attacker_pos -= 1

        ship_table.append({
            CombatColumn.LEFT: '-----',
            CombatColumn.MIDDLE: '-----',
            CombatColumn.RIGHT: '-----'
        })

        for i in range(max(len(defender_fleet_activated[x]) for x in defender_fleet_activated)):
            if i >= len(defender_fleet_activated[CombatColumn.LEFT]):
                left = ''
            else:
                left = str(defender_fleet_activated[CombatColumn.LEFT][i][0])

            if i >= len(defender_fleet_activated[CombatColumn.MIDDLE]):
                middle = ''
            else:
                middle = str(defender_fleet_activated[CombatColumn.MIDDLE][i][0])

            if i >= len(defender_fleet_activated[CombatColumn.RIGHT]):
                right = ''
            else:
                right = str(defender_fleet_activated[CombatColumn.RIGHT][i][0])

            ship_table.append({
                CombatColumn.LEFT: left,
                CombatColumn.MIDDLE: middle,
                CombatColumn.RIGHT: right
            })

        if len(ship_table) != 1:
            rows.append(
                '```\n' + tabulate.tabulate(
                    ship_table,
                    headers={
                        CombatColumn.LEFT: 'Left',
                        CombatColumn.MIDDLE: 'Middle',
                        CombatColumn.RIGHT: 'Right',
                    },
                    tablefmt='github',
                    stralign='center'
                ) + '\n```'
            )

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

    async def send_message(self, channel: discord.TextChannel):
        """
        Send the message to the given channel
        :param channel:
        :return:
        """
        message = await channel.send(str(self))
        self.message = message

        return message

    async def update_message(self):
        """
        Update the current message
        :return:
        """
        await self.message.edit(content=str(self))

    def resolve_combat_round(self):
        """
        Resolves the current combat round
        :return: list[Str]
        """
        messages = []

        for combat_column in CombatColumn.active_columns():
            lines = ['PROCESSING {}'.format(combat_column.value)]

            attacker_ships = self.attacker_fleet.where_column(combat_column)
            defender_ships = self.defender_fleet.where_column(combat_column)

            if attacker_ships:
                attacker_ships = attacker_ships[0]
            else:
                attacker_ships = FleetColumn(-1)

            if defender_ships:
                defender_ships = defender_ships[0]
            else:
                defender_ships = FleetColumn(-1)

            attacker_attack = attacker_ships.attack
            defender_attack = defender_ships.attack

            if self.combat_round == CombatRound.RAIL_GUN:
                attacker_defence = 0
                defender_defence = 0
            else:
                attacker_defence = attacker_ships.defence
                defender_defence = defender_ships.defence

            lines.append(
                'Attacker has `{}` attack and `{}` defence'.format(
                    attacker_attack,
                    attacker_defence
                )
            )
            lines.append(
                'Defender has `{}` attack and `{}` defence'.format(
                    defender_attack,
                    defender_defence
                )
            )

            if attacker_attack > defender_defence:
                damage = attacker_attack - defender_defence
                lines.append('Attacker deals `{}` damage to defender'.format(damage))

                carry_over, new_lines = defender_ships.take_damage(damage)
                lines += new_lines

                if carry_over > 0:
                    lines.append('{} CARRY OVER DAMAGE HITS WAITING FLEETS'.format(carry_over))
                    for fleet in self.defender_fleet.where_column(CombatColumn.WAITING):
                        _, new_lines = fleet.take_damage(carry_over)
                        lines += new_lines

            if defender_attack > attacker_defence:
                damage = defender_attack - attacker_defence
                lines.append('Defender deals `{}` damage to attacker'.format(damage))

                carry_over, new_lines = attacker_ships.take_damage(damage)
                lines += new_lines

                if carry_over > 0:
                    lines.append('{} CARRY OVER DAMAGE HITS WAITING FLEETS'.format(carry_over))
                    for fleet in self.attacker_fleet.where_column(CombatColumn.WAITING):
                        _, new_lines = fleet.take_damage(carry_over)
                        lines += new_lines

            messages.append('\n'.join(lines))

        return messages
