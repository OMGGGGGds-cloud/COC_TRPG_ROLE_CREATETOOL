"""Call of Cthulhu 7th Edition character creation data.

Defines the standard characteristics and their dice formulas.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CoCCharacteristic:
    """A CoC 7e character characteristic.

    Attributes:
        name: Abbreviated name (e.g., "STR", "CON", "INT").
        formula: Dice notation formula (e.g., "3d6", "2d6+6").
        full_name: Full descriptive name.
        display_order: Order for display purposes.
    """

    name: str
    formula: str
    full_name: str
    display_order: int


# Standard CoC 7th Edition characteristics
COC_CHARACTERISTICS: list[CoCCharacteristic] = [
    CoCCharacteristic("STR", "3d6", "Strength", 1),
    CoCCharacteristic("CON", "3d6", "Constitution", 2),
    CoCCharacteristic("DEX", "3d6", "Dexterity", 3),
    CoCCharacteristic("POW", "3d6", "Power", 4),
    CoCCharacteristic("APP", "3d6", "Appearance", 5),
    CoCCharacteristic("SIZ", "2d6+6", "Size", 6),
    CoCCharacteristic("INT", "2d6+6", "Intelligence", 7),
    CoCCharacteristic("EDU", "2d6+6", "Education", 8),
]
