"""Expected value calculator for dice expressions.

Uses the formula: E[NdX+Y] = N * (X + 1) / 2 + Y
"""

from dice_calc.parser import DiceExpression, parse_notation

# CoC 7e converts raw 3-18 scores to a 15-90 percentile scale by multiplying by 5
COC_PERCENTILE_MULTIPLIER: int = 5


def expected_value(expr: DiceExpression) -> float:
    """Calculate the expected value of a dice expression, multiplied by
    COC_PERCENTILE_MULTIPLIER to convert CoC 7e raw characteristic scores
    to percentile values.

    Formula: E[NdX+Y] = N * (X + 1) / 2 + Y   (raw score)
             Percentile = raw × COC_PERCENTILE_MULTIPLIER

    For example:
        - 3d6 → 3 * (6 + 1) / 2 * 5 = 52.5
        - 2d6+6 → (2 * (6 + 1) / 2 + 6) * 5 = 65.0
        - 5d6 → 5 * (6 + 1) / 2 * 5 = 87.5

    Args:
        expr: The dice expression to evaluate.

    Returns:
        The expected value as a float (percentile scale).
    """
    per_die = (expr.sides + 1) / 2.0
    raw = expr.count * per_die + expr.modifier
    return raw * COC_PERCENTILE_MULTIPLIER


def expected_value_str(notation: str) -> str:
    """Convenience: parse notation and return a formatted string.

    Args:
        notation: A dice notation string (e.g., "3d6").

    Returns:
        A human-readable string with the formula breakdown.
    """
    expr = parse_notation(notation)
    total = expected_value(expr)
    per_die = (expr.sides + 1) / 2.0

    percentile_per_die = per_die * COC_PERCENTILE_MULTIPLIER
    mult_label = f"(×{COC_PERCENTILE_MULTIPLIER})"

    parts = [f"Formula: {expr.notation}"]
    parts.append(f"Expected percentile value: {total:g}")

    detail_parts = []
    if percentile_per_die.is_integer():
        detail_parts.append(f"{int(percentile_per_die)} per die {mult_label}")
    else:
        detail_parts.append(f"{percentile_per_die:g} per die {mult_label}")
    label = "die" if expr.count == 1 else "dice"
    detail_parts.append(f"× {expr.count} {label}")
    if expr.modifier:
        scaled_mod = expr.modifier * COC_PERCENTILE_MULTIPLIER
        detail_parts.append(f"{'+' if scaled_mod > 0 else ''}{scaled_mod} flat {mult_label}")
    parts.append(f"  ({', '.join(detail_parts)})")

    return "\n".join(parts)
