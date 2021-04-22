"""
Fleet module
"""

import enum
import re

from bot_heard_round.ship import Ship, ShipType

add_fleet_ship_regex = re.compile('(.)(\\d+)\\[(\\d+),(\\d+)]')
fleet_column_regex = re.compile('Fleet column (\\d+)')


class CombatColumn(enum.Enum):
    """
    Enum for the different combat columns
    """
    WAITING = 'waiting'
    LEFT = 'left'
    MIDDLE = 'middle'
    RIGHT = 'right'


class FleetColumn:
    """
    Fleet column
    """

    def __init__(self,
                 column_number: int,
                 combat_column: CombatColumn = CombatColumn.WAITING,
                 ships: list[tuple[Ship, int]] = None
                 ):
        if ships is None:
            ships = []

        self.column_number = column_number
        self.combat_column = combat_column
        self.ships = ships

    def add_ship(self, ship: Ship, position: int):
        """

        :param ship:
        :param position:
        """
        self.ships.append((ship, position))

        self.ships.sort(
            key=lambda x: x[1]
        )

    def __str__(self):
        return 'Fleet column {}\nShips: {}'.format(
            self.column_number,
            ', '.join(['`{}`'.format(x[0]) for x in self.ships])
        )

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

        if other.column_number != self.column_number:
            return False

        if other.combat_column != self.combat_column:
            return False

        if len(self.ships) != len(other.ships):
            return False

        for i, ship in enumerate(self.ships):
            other_ship = other.ships[i]
            if ship != other_ship:
                return False

        return True


class FleetList:
    """
    Fleet list encapsulation
    """

    def __init__(self,
                 columns: tuple[
                     FleetColumn,
                     FleetColumn,
                     FleetColumn,
                     FleetColumn,
                     FleetColumn
                 ] = None
                 ):
        if columns is None:
            columns = (
                FleetColumn(1),
                FleetColumn(2),
                FleetColumn(3),
                FleetColumn(4),
                FleetColumn(5),
            )

        self.columns = columns

    @classmethod
    def from_list(cls, fleet_str: str):
        """

        :rtype: FleetList
        """
        fleet = fleet_str.split('|')

        columns = (
            FleetColumn(1),
            FleetColumn(2),
            FleetColumn(3),
            FleetColumn(4),
            FleetColumn(5),
        )

        for ship_def in fleet:
            match = add_fleet_ship_regex.match(ship_def)

            if not match:
                raise ValueError(f'`{ship_def}` in fleet is invalid')

            ship = Ship(
                current_health=int(match.group(2)),
                ship_type=ShipType.from_str(match.group(1))
            )

            (column_num, position) = (int(match.group(3)), int(match.group(4)))

            column_num -= 1

            columns[column_num].add_ship(ship, position)

        return FleetList(columns)

    def where_column(self, combat_column: CombatColumn) -> list[FleetColumn]:
        """

        :param combat_column:
        :return:
        """
        return list(filter(lambda x: x.combat_column == combat_column, self.columns))