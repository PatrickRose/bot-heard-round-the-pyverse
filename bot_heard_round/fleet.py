"""
Fleet module
"""

import enum
import re

from bot_heard_round import emoji
from bot_heard_round.ship import Ship, ShipType

add_fleet_ship_regex = re.compile('(.+?)(\\d+)\\[(\\d+),(\\d+)]')
fleet_column_regex = re.compile('Fleet column (\\d+)')



class CombatColumn(enum.Enum):
    """
    Enum for the different combat columns
    """
    WAITING = 'waiting'
    LEFT = 'Left'
    MIDDLE = 'Middle'
    RIGHT = 'Right'

    @classmethod
    def adjacent_columns(cls, column):
        """

        :rtype: list[CombatColumn]
        """
        return {
            CombatColumn.RIGHT: [CombatColumn.MIDDLE],
            CombatColumn.MIDDLE: [CombatColumn.LEFT, CombatColumn.RIGHT],
            CombatColumn.LEFT: [CombatColumn.MIDDLE],
        }[column]

    @classmethod
    def active_columns(cls):
        """

        :rtype: list[CombatColumn]
        """
        return [
            cls.LEFT,
            cls.MIDDLE,
            cls.RIGHT,
        ]

class FleetColumn:
    """
    Fleet column
    """

    def __init__(self,
                 column_number: int,
                 combat_column: CombatColumn = CombatColumn.WAITING,
                 ships: list[tuple[Ship, int]] = None,
                 fleet_list=None
                 ):
        if ships is None:
            ships = []

        self.column_number = column_number
        self.combat_column = combat_column
        self.ships = ships
        self.fleet_list = fleet_list

    @property
    def defence(self):
        """

        :rtype: int
        """
        defence = sum([x[0].defence for x in self.ships])

        return defence if not self.patrol_mode else defence // 2

    @property
    def attack(self):
        """

        :rtype: int
        """
        attack = sum([x[0].attack for x in self.ships])

        return attack if not self.patrol_mode else attack // 2

    def add_ship(self, ship: Ship, position: int):
        """

        :param ship:
        :param position:
        """
        self.ships.append((ship, position))

        self.ships.sort(
            key=lambda x: x[1]
        )

    @property
    def patrol_mode(self):
        """
        Check if the fleet is in patrol mode or not
        :return: bool
        """
        return self.fleet_list and self.fleet_list.patrol_mode

    def __str__(self):
        return 'Fleet column {}\nShips: {}'.format(
            self.column_number,
            self.ships_as_str
        )

    @property
    def ships_as_str(self):
        """

        :rtype: str
        """
        return ', '.join(['`{}`'.format(x[0]) for x in self.ships])

    @classmethod
    def from_string(cls, string: str):
        """

        :param string:
        :rtype: FleetColumn
        :return:
        """
        split_list = string.split('\n')

        if len(split_list) == 1:
            split_list.append('Ships: ')

        ships: string
        [column_number, ships] = split_list

        column_number_match = fleet_column_regex.match(column_number)

        if not column_number_match:
            raise ValueError('Column number string does not work')

        position = 0
        ship_list = []

        for ship in ships.split(': ')[1].split(','):
            if ship == '':
                continue

            ship_list.append((Ship.from_str(ship), position))
            position += 1

        return FleetColumn(int(column_number_match.group(1)), ships=ship_list)

    def __eq__(self, other):
        if not isinstance(other, FleetColumn):
            return False

        for attr in ['patrol_mode', 'column_number', 'combat_column']:
            if getattr(self, attr) != getattr(other, attr):
                return False

        if len(self.ships) != len(other.ships):
            return False

        for i, ship in enumerate(self.ships):
            other_ship = other.ships[i]
            if ship != other_ship:
                return False

        return True

    def take_damage(self, damage):
        """

        :rtype: tuple[int, str]
        """
        message = []

        while damage > 0:
            if not self.ships:
                break

            ship = self.ships[0]
            if damage >= ship[0].current_health:
                damage -= ship[0].current_health
                message.append("{} {} is destroyed!".format(emoji.BOOM_EMOJI, ship[0]))
                self.ships.remove(ship)
            else:
                message.append("{} takes {} damage".format(ship[0], damage))
                ship[0].current_health -= damage
                damage = 0

        return damage, message


class FleetList:
    """
    Fleet list encapsulation
    """

    class NoWaitingFleetError(OverflowError):
        """
        Error for if there are no waiting fleets
        """

    def __init__(self,
                 columns: tuple[
                     FleetColumn,
                     FleetColumn,
                     FleetColumn,
                     FleetColumn,
                     FleetColumn
                 ] = None,
                 patrol_mode: bool = False
                 ):
        if columns is None:
            columns = (
                FleetColumn(1),
                FleetColumn(2),
                FleetColumn(3),
                FleetColumn(4),
                FleetColumn(5),
            )

        for column in columns:
            column.fleet_list = self

        self.columns = columns
        self.patrol_mode = patrol_mode

    @classmethod
    def from_str(cls, fleet_str: str):
        """

        :rtype: FleetList
        """
        patrol_mode = fleet_str[0:3] == '<P>'
        if patrol_mode:
            fleet_str = fleet_str[3:]

        fleet = fleet_str.split('|')

        columns = (
            FleetColumn(1),
            FleetColumn(2),
            FleetColumn(3),
            FleetColumn(4),
            FleetColumn(5),
        )

        for ship_def in fleet:
            if ship_def == '':
                continue

            match = add_fleet_ship_regex.match(ship_def)

            if not match:
                raise ValueError(f'`{ship_def}` in fleet is invalid')

            ship = Ship(
                current_health=int(match.group(2)),
                ship_type=ShipType.from_char(match.group(1))
            )

            (column_num, position) = (int(match.group(3)), int(match.group(4)))

            column_num -= 1

            columns[column_num].add_ship(ship, position)

        return FleetList(columns, patrol_mode=patrol_mode)

    def where_column(self, combat_column: CombatColumn) -> list[FleetColumn]:
        """

        :param combat_column:
        :return:
        """
        return list(filter(lambda x: x.combat_column == combat_column, self.columns))

    def __eq__(self, other):
        if not isinstance(other, FleetList):
            return False

        for attr in ['patrol_mode', 'columns']:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

    def __str__(self):
        patrol_mode = ['PATROL MODE'] if self.patrol_mode else []

        return '\n'.join(patrol_mode + [str(x) for x in self.columns])

    def swap_options(self):
        """
        Get the list of options for swapping
        :return:
        """
        waiting_fleet = list(
            filter(
                lambda waiting_column: waiting_column.ships,
                self.where_column(CombatColumn.WAITING),
            )
        )

        if not waiting_fleet:
            raise FleetList.NoWaitingFleetError

        emojis_to_add = {
            emoji.CROSS_EMOJI: None
        }
        column_to_emoji = {
            CombatColumn.LEFT: emoji.LEFT_EMOJI,
            CombatColumn.MIDDLE: emoji.CENTRE_EMOJI,
            CombatColumn.RIGHT: emoji.RIGHT_EMOJI,
        }

        for column in CombatColumn.active_columns():
            fleet_column = self.where_column(column)

            if fleet_column:
                emojis_to_add[column_to_emoji[column]] = fleet_column[0].column_number

        ship_list = {}

        for waiting in waiting_fleet:
            emoji_to_send = emoji.POSSIBLE_EMOJI[waiting.column_number - 1]

            ship_list[emoji_to_send] = waiting.column_number

        return (
            emojis_to_add,
            ship_list
        )

    def where_number(self, column_number: int):
        """

        :param column_number:
        :return:
        """
        for fleet in self.columns:
            if fleet.column_number == column_number:
                return fleet

        raise IndexError

    def swap_columns(self, to_swap_out: int, to_swap_in: int):
        """
        Swap the columns
        :param to_swap_out:
        :param to_swap_in:
        :return:
        """
        swap_out = self.where_number(to_swap_out)
        swap_in = self.where_number(to_swap_in)

        swap_out_combat_column = swap_out.combat_column
        swap_out.combat_column = swap_in.combat_column
        swap_in.combat_column = swap_out_combat_column
