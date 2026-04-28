"""Dice notation parser.

Parses standard dice notation like "3d6", "2d6+6", "5d6", "4d4-2".
"""

import re
from dataclasses import dataclass

_DICE_PATTERN = re.compile(r"^(\d+)d(\d+)([+-]\d+)?$")


@dataclass(frozen=True)
class DiceExpression:
    """A parsed dice expression.

    Attributes:
        count: Number of dice to roll (e.g., 3 in "3d6").
        sides: Number of sides per die (e.g., 6 in "3d6").
        modifier: Flat modifier added to the sum (0 if absent).
    """

    count: int
    sides: int
    modifier: int = 0

    @property
    def notation(self) -> str:
        """Return the canonical notation string."""
        base = f"{self.count}d{self.sides}"
        if self.modifier > 0:
            return f"{base}+{self.modifier}"
        if self.modifier < 0:
            return f"{base}{self.modifier}"
        return base

    def __str__(self) -> str:
        return self.notation


def parse_notation(notation: str) -> DiceExpression:
    """Parse a dice notation string into a DiceExpression.

    Args:
        notation: A dice notation string (e.g., "3d6", "2d6+6", "5d6").

    Returns:
        A DiceExpression with the parsed values.

    Raises:
        ValueError: If the notation is invalid.
    """
    notation = notation.strip().lower()
    match = _DICE_PATTERN.match(notation)
    if not match:
        raise ValueError(
            f"Invalid dice notation: '{notation}'. "
            f"Expected format like '3d6', '2d6+6', or '5d6'."
        )

    count = int(match.group(1))
    sides = int(match.group(2))
    modifier_str = match.group(3)
    modifier = int(modifier_str) if modifier_str else 0

    if count < 1:
        raise ValueError(f"Number of dice must be at least 1, got {count}.")
    if sides < 2:
        raise ValueError(f"Number of sides must be at least 2, got {sides}.")

    return DiceExpression(count=count, sides=sides, modifier=modifier)
