"""
Ship module
"""

import enum
import re

fleet_ship_regex = re.compile('(.+) \\((\\d+)/\\d+\\)')


class ShipType(enum.Enum):
    """
    Enum for the various ship types
    """
    BATTLESHIP = 'Battleship'
    BATTLECRUISER = 'Battlecruiser'
    HEAVY_CRUISER = 'Heavy Cruiser'
    LIGHT_CRUISER = 'Light Cruiser'
    FRIGATE = 'Frigate'
    DESTROYER = 'Destroyer'
    CORVETTE = 'Corvette'
    SYSTEM_DEFENCE_BOAT = 'System Defence Boat'
    FAC_SQUADRON = 'FAC Squadron'
    ARMED_MERCHANT = 'Armed Merchant'
    STEALTH_ATTACK_SHIP = 'Stealth Attack Ship'
    PD_CRUISER = 'PD Cruiser'
    ASSAULT_LANDING_SHIP = 'Assault Landing Ship'
    FAST_REPLENISHMENT_SHIP = 'Fast Replenishment Ship'
    PATROL_SHIP = 'Patrol Ship'
    SURVEY_SHIP = 'Survey Ship'

    def __str__(self):
        str_rep = {
            ShipType.BATTLESHIP: 'Battleship',
            ShipType.BATTLECRUISER: 'Battlecruiser',
            ShipType.HEAVY_CRUISER: 'Heavy Cruiser',
            ShipType.LIGHT_CRUISER: 'Light Cruiser',
            ShipType.FRIGATE: 'Frigate',
            ShipType.DESTROYER: 'Destroyer',
            ShipType.CORVETTE: 'Corvette',
            ShipType.SYSTEM_DEFENCE_BOAT: 'System Defence Boat',
            ShipType.FAC_SQUADRON: 'FAC Squadron',
            ShipType.ARMED_MERCHANT: 'Armed Merchant',
            ShipType.STEALTH_ATTACK_SHIP: 'Stealth Attack Ship',
            ShipType.PD_CRUISER: 'PD Cruiser',
            ShipType.ASSAULT_LANDING_SHIP: 'Assault Landing Ship',
            ShipType.FAST_REPLENISHMENT_SHIP: 'Fast Replenishment Ship',
            ShipType.PATROL_SHIP: 'Patrol Ship',
            ShipType.SURVEY_SHIP: 'Survey Ship',
        }

        return str_rep[self]

    def to_char(self):
        """
        :return:
        """
        str_rep = {
            ShipType.BATTLESHIP: 'BS',
            ShipType.BATTLECRUISER: 'BC',
            ShipType.HEAVY_CRUISER: 'HC',
            ShipType.LIGHT_CRUISER: 'LC',
            ShipType.FRIGATE: 'F',
            ShipType.DESTROYER: 'D',
            ShipType.CORVETTE: 'C',
            ShipType.SYSTEM_DEFENCE_BOAT: 'SDB',
            ShipType.FAC_SQUADRON: 'FAC',
            ShipType.ARMED_MERCHANT: 'AM',
            ShipType.STEALTH_ATTACK_SHIP: 'SAS',
            ShipType.PD_CRUISER: 'PDC',
            ShipType.ASSAULT_LANDING_SHIP: 'ALS',
            ShipType.FAST_REPLENISHMENT_SHIP: 'FRS',
            ShipType.PATROL_SHIP: 'PS',
            ShipType.SURVEY_SHIP: 'SS',
        }

        return str_rep[self]

    @classmethod
    def from_char(cls, char: str):
        """

        :param char:
        :return:
        """
        str_rep = {
            'BS': ShipType.BATTLESHIP,
            'BC': ShipType.BATTLECRUISER,
            'HC': ShipType.HEAVY_CRUISER,
            'LC': ShipType.LIGHT_CRUISER,
            'F': ShipType.FRIGATE,
            'D': ShipType.DESTROYER,
            'C': ShipType.CORVETTE,
            'SDB': ShipType.SYSTEM_DEFENCE_BOAT,
            'FAC': ShipType.FAC_SQUADRON,
            'AM': ShipType.ARMED_MERCHANT,
            'SAS': ShipType.STEALTH_ATTACK_SHIP,
            'PDC': ShipType.PD_CRUISER,
            'ALS': ShipType.ASSAULT_LANDING_SHIP,
            'FRS': ShipType.FAST_REPLENISHMENT_SHIP,
            'PS': ShipType.PATROL_SHIP,
            'SS': ShipType.SURVEY_SHIP,
        }

        return str_rep[char]

    @classmethod
    def from_str(cls, from_str: str):
        """

        :param from_str:
        :return:
        """
        str_rep = {
            'Battleship': ShipType.BATTLESHIP,
            'Battlecruiser': ShipType.BATTLECRUISER,
            'Heavy Cruiser': ShipType.HEAVY_CRUISER,
            'Light Cruiser': ShipType.LIGHT_CRUISER,
            'Frigate': ShipType.FRIGATE,
            'Destroyer': ShipType.DESTROYER,
            'Corvette': ShipType.CORVETTE,
            'System Defence Boat': ShipType.SYSTEM_DEFENCE_BOAT,
            'FAC Squadron': ShipType.FAC_SQUADRON,
            'Armed Merchant': ShipType.ARMED_MERCHANT,
            'Stealth Attack Ship': ShipType.STEALTH_ATTACK_SHIP,
            'PD Cruiser': ShipType.PD_CRUISER,
            'Assault Landing Ship': ShipType.ASSAULT_LANDING_SHIP,
            'Fast Replenishment Ship': ShipType.FAST_REPLENISHMENT_SHIP,
            'Patrol Ship': ShipType.PATROL_SHIP,
            'Survey Ship': ShipType.SURVEY_SHIP,
        }

        return str_rep[from_str]

    @property
    def max_health(self) -> int:
        """
        Gets the max health for this ship type
        :return:
        """
        return SHIP_MAX_HEALTHS[self]

    @property
    def attack(self):
        """
        Gets the attack value for this ship type
        :return:
        """
        return SHIP_ATTACKS[self]

    @property
    def defence(self):
        """
        Gets the defence value for this ship type
        :return:
        """
        return SHIP_DEFENCES[self]


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

    def __getattr__(self, attr):
        """
        Proxy calls down to the ship type
        :param attr:
        :return:
        """
        return getattr(self.ship_type, attr)

    @classmethod
    def from_str(cls, ship_str: str):
        """

        :param ship_str:
        :rtype: Ship
        :return:
        """
        match = fleet_ship_regex.match(ship_str.strip().strip('`'))

        if not match:
            raise ValueError(f'\'{ship_str}\' did not look valid!')

        return Ship(int(match.group(2)), ShipType.from_str(match.group(1)))

    def __eq__(self, other):
        return isinstance(other, Ship) \
               and other.ship_type == self.ship_type \
               and other.current_health == self.current_health


SHIP_MAX_HEALTHS = {
    ShipType.BATTLESHIP: 30,
    ShipType.BATTLECRUISER: 20,
    ShipType.HEAVY_CRUISER: 20,
    ShipType.LIGHT_CRUISER: 15,
    ShipType.FRIGATE: 10,
    ShipType.DESTROYER: 8,
    ShipType.CORVETTE: 6,
    ShipType.SYSTEM_DEFENCE_BOAT: 6,
    ShipType.FAC_SQUADRON: 2,
    ShipType.ARMED_MERCHANT: 3,
    ShipType.STEALTH_ATTACK_SHIP: 3,
    ShipType.PD_CRUISER: 15,
    ShipType.ASSAULT_LANDING_SHIP: 6,
    ShipType.FAST_REPLENISHMENT_SHIP: 5,
    ShipType.PATROL_SHIP: 2,
    ShipType.SURVEY_SHIP: 2,
}

SHIP_DEFENCES = {
    ShipType.BATTLESHIP: 20,
    ShipType.BATTLECRUISER: 15,
    ShipType.HEAVY_CRUISER: 12,
    ShipType.LIGHT_CRUISER: 8,
    ShipType.FRIGATE: 6,
    ShipType.DESTROYER: 4,
    ShipType.CORVETTE: 4,
    ShipType.SYSTEM_DEFENCE_BOAT: 4,
    ShipType.FAC_SQUADRON: 1,
    ShipType.ARMED_MERCHANT: 2,
    ShipType.STEALTH_ATTACK_SHIP: 1,
    ShipType.PD_CRUISER: 10,
    ShipType.ASSAULT_LANDING_SHIP: 4,
    ShipType.FAST_REPLENISHMENT_SHIP: 3,
    ShipType.PATROL_SHIP: 1,
    ShipType.SURVEY_SHIP: 0,
}

SHIP_ATTACKS = {
    ShipType.BATTLESHIP: 25,
    ShipType.BATTLECRUISER: 25,
    ShipType.HEAVY_CRUISER: 15,
    ShipType.LIGHT_CRUISER: 10,
    ShipType.FRIGATE: 8,
    ShipType.DESTROYER: 6,
    ShipType.CORVETTE: 4,
    ShipType.SYSTEM_DEFENCE_BOAT: 4,
    ShipType.FAC_SQUADRON: 4,
    ShipType.ARMED_MERCHANT: 3,
    ShipType.STEALTH_ATTACK_SHIP: 3,
    ShipType.PD_CRUISER: 2,
    ShipType.ASSAULT_LANDING_SHIP: 2,
    ShipType.FAST_REPLENISHMENT_SHIP: 1,
    ShipType.PATROL_SHIP: 1,
    ShipType.SURVEY_SHIP: 0,
}
