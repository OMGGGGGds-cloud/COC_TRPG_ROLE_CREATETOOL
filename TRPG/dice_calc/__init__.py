"""Dice calculation tools for TRPG character creation analysis."""

from dice_calc.parser import DiceExpression, parse_notation
from dice_calc.calculator import expected_value, expected_value_str
from dice_calc.distribution import dice_sum_distribution, expected_max_of_k
from dice_calc.coc_data import COC_CHARACTERISTICS, CoCCharacteristic
from dice_calc.comparator import ComparisonResult, compare_roll_vs_buy
from dice_calc.cli import run_cli

__all__ = [
    "DiceExpression",
    "parse_notation",
    "expected_value",
    "expected_value_str",
    "dice_sum_distribution",
    "expected_max_of_k",
    "COC_CHARACTERISTICS",
    "CoCCharacteristic",
    "ComparisonResult",
    "compare_roll_vs_buy",
    "run_cli",
]
