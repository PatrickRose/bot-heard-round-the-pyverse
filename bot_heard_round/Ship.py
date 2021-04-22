import enum
import re

fleet_ship_regex = re.compile('`(.+) \((\\d+)/\\d+\)`')


class ShipType(enum.Enum):
    CRUISER = 'Cruiser'
    FIGHTER = 'Fighter'

    def __str__(self):
        str_rep = {
            ShipType.FIGHTER: 'Fighter',
            ShipType.CRUISER: 'Cruiser'
        }

        return str_rep[self]

    @classmethod
    def from_str(cls, from_str):
        str_rep = {
            'Fighter': ShipType.FIGHTER,
            'Cruiser': ShipType.CRUISER,
        }

        return str_rep[from_str]


class Ship:

    def __init__(self, current_health: int, ship_type: ShipType):
        self.current_health = current_health
        self.ship_type = ship_type

    def __str__(self):
        return '{} ({}/{})'.format(
            self.ship_type,
            self.current_health,
            self.max_health()
        )

    def max_health(self):
        return 10

    @classmethod
    def from_str(cls, ship_str):
        match = fleet_ship_regex.match(ship_str.strip())

        if not match:
            raise ValueError(f'\'{ship_str}\' did not look valid!')

        return Ship(int(match.group(2)), ShipType.from_str(match.group(1)))

    def __eq__(self, other):
        return isinstance(other, Ship)\
               and other.ship_type == self.ship_type\
               and other.current_health == self.current_health
