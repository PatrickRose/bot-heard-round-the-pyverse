import enum
import re

import discord
import tabulate

from bot_heard_round.CombatColumn import CombatColumn
from bot_heard_round.Fleet import FleetList, Position
from bot_heard_round.Ship import Ship

attack_defend_regex = re.compile('(Attacker|Defender): `(.+)`')
round_regex = re.compile('`!!! Combat status( - round (\\d)| - finished)? !!!`')
fleet_list_regex = re.compile('(Attacker|Defender) ships to apply: (.+)')
ship_regex = re.compile('`(.+?) \\((\\w+) (\\d+)/(\\d+)\\)`')


class CombatRound(enum.Enum):
    PENDING = 0,
    MISSILE_ONE = 1,
    MISSILE_TWO = 2,
    RAILGUN = 3
    FINISHED = 4


class CombatStatus:

    def __init__(self, attacker: discord.User,
                 defender: discord.User,
                 attacker_fleet: FleetList = None,
                 defender_fleet: FleetList = None,
                 combat_round=CombatRound.PENDING):
        if attacker_fleet is None:
            attacker_fleet = FleetList()
        if defender_fleet is None:
            defender_fleet = FleetList()

        self.attacker = attacker
        self.defender = defender
        self.attacker_fleet = attacker_fleet
        self.defender_fleet = defender_fleet
        self.combat_round = combat_round

    def add_fleet_for(self, user: discord.User, fleet: str):
        if user.id == self.attacker.id:
            self.attacker_fleet = FleetList.from_list(fleet)
        else:
            self.defender_fleet = FleetList.from_list(fleet)

    def __str__(self):
        attacker = self.attacker.nick or self.attacker.name
        defender = self.defender.nick or self.defender.name

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
        elif self.combat_round == CombatRound.RAILGUN:
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
                    '\n'.join(['`{}`'.format(str(x)) for x in attacker_fleet_waiting])
                )
            )

        if defender_fleet_waiting:
            rows.append(
                "Defender ships to apply:\n{}".format(
                    '\n'.join(['`{}`'.format(str(x)) for x in defender_fleet_waiting])
                )
            )

        attacker_fleet_ready = self.attacker_fleet.where_column(CombatColumn.MIDDLE)
        defender_fleet_ready = self.defender_fleet.where_column(CombatColumn.MIDDLE)

        if attacker_fleet_ready or defender_fleet_ready:
            attacker_fleet_ready.sort(key=lambda x: x[1].position, reverse=True)
            defender_fleet_ready.sort(key=lambda x: x[1].position)

            rows.append(
                '```\n' + tabulate.tabulate(
                    [str(x[0]) for x in attacker_fleet_ready] + ['------'] + [str(x[0]) for x in defender_fleet_ready]
                ) + '\n```'
            )

        return "\n".join(rows)

    def ready_for_combat(self):
        return self.attacker_fleet.ships and self.defender_fleet.ships

    @classmethod
    async def from_message(cls, message: discord.Message):
        content = message.content
        attacker: discord.User
        defender: discord.User
        defender_ships = FleetList()
        attacker_ships = FleetList()

        members = await message.guild.fetch_members().flatten()

        for line in content.split("\n"):

            match = round_regex.match(line)
            if match:
                if match.group(2) is None:
                    combat_round = CombatRound.PENDING if match.group(1) is None else CombatRound.FINISHED
                else:
                    combat_round = [
                        'EMPTY',
                        CombatRound.MISSILE_ONE,
                        CombatRound.MISSILE_TWO,
                        CombatRound.RAILGUN
                    ][int(match.group(2))]

            match = attack_defend_regex.match(line)

            if match:
                attack_defend = match.group(1)
                name_nick = match.group(2)

                user = discord.utils.get(members, nick=name_nick)

                if not user:
                    user = discord.utils.get(members, name=name_nick)

                if not user:
                    raise ValueError('Could not find user with name/nickname {}'.format(name_nick))

                if attack_defend == 'Attacker':
                    attacker = user
                else:
                    defender = user

            match = fleet_list_regex.match(line)

            if match:
                attack_defend = match.group(1)
                ships = match.group(2)
                if attack_defend == 'Attacker':
                    ship_list = attacker_ships
                else:
                    ship_list = defender_ships

                for group in ship_regex.finditer(ships):
                    ship = Ship(name=group[1], ship_type=group[2], current_health=group[3], max_health=group[4])

                    ship_list.add_ship(ship, Position(CombatColumn.WAITING, -1))

        return CombatStatus(attacker, defender, attacker_ships, defender_ships, combat_round=combat_round)
