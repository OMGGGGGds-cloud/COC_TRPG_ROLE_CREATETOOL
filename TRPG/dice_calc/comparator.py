"""Roll vs. Point-Buy comparison for CoC 7e character creation.

Provides comparison modes:
    - Mode A ("full_set"):  Roll K complete attribute sets, pick the set with
      the highest total.
    - Mode B ("per_group"): Roll K complete attribute sets, then pool all
      3d6-type rolls together and pick the best 5, and pool all 2d6+6-type
      rolls together and pick the best 3.

All calculations use exact probability math (order statistics via convolutions
of dice sum distributions). No random simulation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dice_calc.parser import parse_notation
from dice_calc.calculator import expected_value
from dice_calc.distribution import (
    dice_sum_distribution_with_modifier,
    expected_max_of_k,
    expected_sum_of_top_k,
    convolve_distributions,
)
from dice_calc.coc_data import COC_CHARACTERISTICS, CoCCharacteristic

# Group definitions for Mode B: 3d6-type and 2d6+6-type characteristics
_3D6_CHARACTERISTICS: List[CoCCharacteristic] = [
    c for c in COC_CHARACTERISTICS if c.formula == "3d6"
]
_2D6_CHARACTERISTICS: List[CoCCharacteristic] = [
    c for c in COC_CHARACTERISTICS if c.formula == "2d6+6"
]
COUNT_3D6: int = len(_3D6_CHARACTERISTICS)    # 5
COUNT_2D6: int = len(_2D6_CHARACTERISTICS)    # 3


@dataclass
class AttributeComparison:
    """Results for a single attribute in the comparison."""

    characteristic: CoCCharacteristic
    expected_single: float
    expected_best_of_k: float


@dataclass
class ComparisonResult:
    """Overall results of a roll vs. point-buy comparison."""

    point_buy_budget: float
    attempts: int
    mode: str

    # Overall summary
    expected_best_total: float
    point_buy_total: float

    # Per-attribute breakdown
    attributes: List[AttributeComparison] = field(default_factory=list)

    # Full-set distribution info (Mode A only)
    set_distribution: Optional[Dict[int, float]] = None
    single_set_expected: Optional[float] = None

    # Per-group breakdown (Mode B only)
    group_3d6_expected_best: Optional[float] = None
    """Expected sum of best 5 selected 3d6 rolls."""
    group_2d6_expected_best: Optional[float] = None
    """Expected sum of best 3 selected 2d6+6 rolls."""
    group_3d6_pool_size: Optional[int] = None
    """Number of 3d6-type rolls in the pool (5 × attempts)."""
    group_2d6_pool_size: Optional[int] = None
    """Number of 2d6+6-type rolls in the pool (3 × attempts)."""

    @property
    def difference(self) -> float:
        """Positive means rolling is better; negative means buying is better."""
        return self.expected_best_total - self.point_buy_total

    @property
    def recommendation(self) -> str:
        if self.difference > 0:
            return (
                f"Rolling beats buying by {self.difference:.1f} points. "
                f"With {self.attempts} attempt(s), rolling yields a better expected outcome."
            )
        elif self.difference < 0:
            return (
                f"Buying beats rolling by {abs(self.difference):.1f} points. "
                f"The point-buy budget gives a better guaranteed outcome."
            )
        else:
            return "Both approaches yield the same expected outcome."


def _build_attribute_distribution(char: CoCCharacteristic) -> Dict[int, float]:
    """Build the exact probability distribution for a characteristic.

    Returns the distribution of raw characteristic scores (not percentile).
    """
    expr = parse_notation(char.formula)
    return dice_sum_distribution_with_modifier(expr.count, expr.sides, expr.modifier)


def _expected_value_from_formula(formula: str) -> float:
    """Get the expected value from a dice formula string.

    Returns the raw expected characteristic score (not percentile).
    """
    expr = parse_notation(formula)
    return expected_value(expr)


def compare_mode_full_set(
    budget: float, attempts: int
) -> ComparisonResult:
    """Mode A: Roll K complete attribute sets, pick best by total sum.

    Computes the distribution of the total sum of one 8-attribute set,
    then uses order statistics to find the expected maximum over K sets.

    Args:
        budget: Point-buy budget (total points available).
        attempts: Number of complete sets to roll (K).

    Returns:
        A ComparisonResult with full-set analysis.
    """
    # Build distributions for each characteristic
    attr_dists = [_build_attribute_distribution(char) for char in COC_CHARACTERISTICS]

    # Convolve all 8 into the total set distribution
    set_dist = convolve_distributions(attr_dists)

    # Expected total of a single set
    single_expected = sum(
        _expected_value_from_formula(char.formula) for char in COC_CHARACTERISTICS
    )

    # Expected max over K sets (multiply by 5 for percentile scale)
    expected_best = expected_max_of_k(set_dist, attempts) * 5

    # single_expected comes from expected_value() which already returns ×5
    return ComparisonResult(
        point_buy_budget=budget,
        attempts=attempts,
        mode="full_set",
        expected_best_total=expected_best,
        point_buy_total=budget,
        single_set_expected=single_expected,
        set_distribution=set_dist,
    )


def _build_single_group_distribution(
    chars: List[CoCCharacteristic],
) -> Dict[int, float]:
    """Build the distribution for a single roll from a group of characteristics.

    All characteristics in the group share the same formula (e.g. all 3d6).
    Returns the distribution of a single raw roll (any characteristic).

    Args:
        chars: List of characteristics that share the same formula.

    Returns:
        The raw distribution for a single roll.
    """
    if not chars:
        return {0: 1.0}
    # All chars in a group share the same formula (by construction)
    return _build_attribute_distribution(chars[0])


def _expected_value_group(chars: List[CoCCharacteristic]) -> float:
    """Expected value (raw) for a single roll from a group.

    Args:
        chars: List of characteristics sharing the same formula.

    Returns:
        Expected value of one characteristic's raw roll.
    """
    if not chars:
        return 0.0
    return _expected_value_from_formula(chars[0].formula)


def compare_mode_per_group(
    budget: float,
    attempts: int,
) -> ComparisonResult:
    """Mode B: Roll K complete sets, pool by formula group, pick best per group.

    Procedure:
        1. Roll K complete attribute sets (each set = 5×3d6 + 3×2d6+6).
        2. Pool all 3d6 rolls: N3 = 5×K draws from the 3d6 distribution.
           Pick the best 5 from this pool.
        3. Pool all 2d6+6 rolls: N2 = 3×K draws from the 2d6+6 distribution.
           Pick the best 3 from this pool.
        4. Sum the 8 selected values for the final total.

    Args:
        budget: Point-buy budget (total points available).
        attempts: Number of complete sets to roll (K).

    Returns:
        A ComparisonResult with per-group analysis.
    """
    # Build distributions for each formula group
    dist_3d6 = _build_single_group_distribution(_3D6_CHARACTERISTICS)
    dist_2d6 = _build_single_group_distribution(_2D6_CHARACTERISTICS)

    # Pool sizes
    pool_3d6 = COUNT_3D6 * attempts   # 5 × K
    pool_2d6 = COUNT_2D6 * attempts   # 3 × K

    # Expected sum of best 5 out of 5K 3d6 rolls (multiply by 5 for percentile scale)
    expected_best_3d6 = expected_sum_of_top_k(dist_3d6, pool_3d6, COUNT_3D6) * 5

    # Expected sum of best 3 out of 3K 2d6+6 rolls (multiply by 5 for percentile scale)
    expected_best_2d6 = expected_sum_of_top_k(dist_2d6, pool_2d6, COUNT_2D6) * 5

    expected_best_total = expected_best_3d6 + expected_best_2d6

    # Single-set expected total (for reference)
    single_expected = sum(
        _expected_value_from_formula(char.formula) for char in COC_CHARACTERISTICS
    )

    return ComparisonResult(
        point_buy_budget=budget,
        attempts=attempts,
        mode="per_group",
        expected_best_total=expected_best_total,
        point_buy_total=budget,
        single_set_expected=single_expected,
        group_3d6_expected_best=expected_best_3d6,
        group_2d6_expected_best=expected_best_2d6,
        group_3d6_pool_size=pool_3d6,
        group_2d6_pool_size=pool_2d6,
    )





def compare_roll_vs_buy(
    budget: float,
    attempts: int,
    mode: str = "full_set",
) -> ComparisonResult:
    """Compare rolling dice vs. point-buy for CoC 7e character creation.

    Args:
        budget: Point-buy budget (total points available to allocate).
        attempts: Number of attempts/sets to roll (K).
        mode: Comparison mode — "full_set" (Mode A, default) or
              "per_group" (Mode B).

    Returns:
        A ComparisonResult with the analysis.

    Raises:
        ValueError: If budget < 0, attempts < 1, or mode is invalid.
    """
    if budget < 0:
        raise ValueError(f"Budget must be >= 0, got {budget}.")
    if attempts < 1:
        raise ValueError(f"Attempts must be >= 1, got {attempts}.")
    valid_modes = {"full_set", "per_group"}
    if mode not in valid_modes:
        raise ValueError(f"Mode must be one of {valid_modes}, got '{mode}'.")

    if mode == "full_set":
        return compare_mode_full_set(budget, attempts)
    elif mode == "per_group":
        return compare_mode_per_group(budget, attempts)
    else:
        # Should not be reached due to validation above
        raise ValueError(f"Unknown mode '{mode}'.")
