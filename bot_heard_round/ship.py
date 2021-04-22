"""
Ship module
"""

import enum
import re

fleet_ship_regex = re.compile('`(.+) \\((\\d+)/\\d+\\)`')


class ShipType(enum.Enum):
    """
    Enum for the various ship types
    """
    CRUISER = 'Cruiser'
    FIGHTER = 'Fighter'

    def __str__(self):
        str_rep = {
            ShipType.FIGHTER: 'Fighter',
            ShipType.CRUISER: 'Cruiser'
        }

        return str_rep[self]

    @classmethod
    def from_str(cls, from_str: str):
        """

        :param from_str:
        :return:
        """
        str_rep = {
            'Fighter': ShipType.FIGHTER,
            'Cruiser': ShipType.CRUISER,
        }

        return str_rep[from_str]

    @property
    def max_health(self) -> int:
        """
        Gets the max health for this ship type
        :return:
        """
        return 10


class Ship:
    """
    Class to represent a ship
    """

    def __init__(self, current_health: int, ship_type: ShipType):
        self.current_health = current_health
        self.ship_type = ship_type

    def __str__(self):
        return '{} ({}/{})'.format(
            self.ship_type,
            self.current_health,
            self.max_health
        )

    @property
    def max_health(self) -> int:
        """
        Proxies to the ship type enum's max health
        :return:
        """
        return self.ship_type.max_health

    @classmethod
    def from_str(cls, ship_str: str):
        """

        :param ship_str:
        :rtype: Ship
        :return:
        """
        match = fleet_ship_regex.match(ship_str.strip())

        if not match:
            raise ValueError(f'\'{ship_str}\' did not look valid!')

        return Ship(int(match.group(2)), ShipType.from_str(match.group(1)))

    def __eq__(self, other):
        return isinstance(other, Ship)\
               and other.ship_type == self.ship_type\
               and other.current_health == self.current_health
