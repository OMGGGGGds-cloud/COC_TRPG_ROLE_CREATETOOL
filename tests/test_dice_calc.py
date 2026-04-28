"""Unit tests for the dice_calc package."""

import pytest
import math
from dice_calc.parser import parse_notation, DiceExpression
from dice_calc.calculator import expected_value, expected_value_str
from dice_calc.distribution import (
    dice_sum_distribution,
    dice_sum_distribution_with_modifier,
    cumulative_distribution,
    expected_max_of_k,
    expected_sum_of_top_k,
    convolve_distributions,
)
from dice_calc.coc_data import COC_CHARACTERISTICS
from dice_calc.comparator import compare_roll_vs_buy


# =============================================================================
# Parser Tests
# =============================================================================

class TestParseNotation:
    def test_simple_notation(self):
        expr = parse_notation("3d6")
        assert expr == DiceExpression(count=3, sides=6, modifier=0)

    def test_notation_with_modifier(self):
        expr = parse_notation("2d6+6")
        assert expr == DiceExpression(count=2, sides=6, modifier=6)

    def test_notation_with_negative_modifier(self):
        expr = parse_notation("4d4-2")
        assert expr == DiceExpression(count=4, sides=4, modifier=-2)

    def test_five_dice(self):
        expr = parse_notation("5d6")
        assert expr == DiceExpression(count=5, sides=6, modifier=0)

    def test_single_die(self):
        expr = parse_notation("1d20")
        assert expr == DiceExpression(count=1, sides=20, modifier=0)

    def test_notation_string_representation(self):
        expr = DiceExpression(count=3, sides=6)
        assert str(expr) == "3d6"
        assert expr.notation == "3d6"

    def test_notation_string_with_modifier(self):
        expr = DiceExpression(count=2, sides=6, modifier=6)
        assert str(expr) == "2d6+6"

    def test_notation_string_negative_modifier(self):
        expr = DiceExpression(count=4, sides=4, modifier=-2)
        assert str(expr) == "4d4-2"

    def test_notation_zero_modifier(self):
        expr = DiceExpression(count=3, sides=6, modifier=0)
        assert str(expr) == "3d6"

    def test_case_insensitivity(self):
        expr = parse_notation("3D6")
        assert expr == DiceExpression(count=3, sides=6, modifier=0)

    def test_whitespace_handling(self):
        expr = parse_notation("  3d6  ")
        assert expr == DiceExpression(count=3, sides=6, modifier=0)

    # --- Error cases ---

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid dice notation"):
            parse_notation("abc")

    def test_missing_count(self):
        with pytest.raises(ValueError, match="Invalid dice notation"):
            parse_notation("d6")

    def test_zero_count(self):
        with pytest.raises(ValueError, match="Number of dice must be at least 1"):
            parse_notation("0d6")

    def test_one_sided_die(self):
        with pytest.raises(ValueError, match="Number of sides must be at least 2"):
            parse_notation("3d1")

    def test_incomplete_modifier(self):
        with pytest.raises(ValueError, match="Invalid dice notation"):
            parse_notation("3d6+")

    def test_multiple_modifiers(self):
        with pytest.raises(ValueError, match="Invalid dice notation"):
            parse_notation("3d6+6+2")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="Invalid dice notation"):
            parse_notation("")


# =============================================================================
# Calculator Tests
# =============================================================================

class TestExpectedValue:
    def test_3d6(self):
        # 3 * (6+1)/2 * 5 = 10.5 * 5 = 52.5
        assert expected_value(parse_notation("3d6")) == 52.5

    def test_2d6_plus_6(self):
        # (2 * (6+1)/2 + 6) * 5 = 13.0 * 5 = 65.0
        assert expected_value(parse_notation("2d6+6")) == 65.0

    def test_5d6(self):
        # 5 * (6+1)/2 * 5 = 17.5 * 5 = 87.5
        assert expected_value(parse_notation("5d6")) == 87.5

    def test_1d20(self):
        # 1 * (20+1)/2 * 5 = 10.5 * 5 = 52.5
        assert expected_value(parse_notation("1d20")) == 52.5

    def test_4d4_minus_2(self):
        # (4 * (4+1)/2 - 2) * 5 = 8.0 * 5 = 40.0
        assert expected_value(parse_notation("4d4-2")) == 40.0

    def test_3d8(self):
        # 3 * (8+1)/2 * 5 = 13.5 * 5 = 67.5
        assert expected_value(parse_notation("3d8")) == 67.5

    def test_single_die(self):
        # 1 * (6+1)/2 * 5 = 3.5 * 5 = 17.5
        assert expected_value(parse_notation("1d6")) == 17.5

    def test_large_number_of_dice(self):
        # 100d6 = 100 * 3.5 * 5 = 1750
        assert expected_value(parse_notation("100d6")) == 1750.0

    def test_expected_value_str_format(self):
        result = expected_value_str("3d6")
        assert "Expected percentile value: 52.5" in result
        assert "3d6" in result or "3d6" in result


# =============================================================================
# Distribution Tests
# =============================================================================

class TestDiceSumDistribution:
    def test_single_die_uniform(self):
        dist = dice_sum_distribution(1, 6)
        assert len(dist) == 6
        for i in range(1, 7):
            assert dist[i] == pytest.approx(1.0 / 6)

    def test_two_dice_sum_to_one(self):
        dist = dice_sum_distribution(2, 6)
        total_prob = sum(dist.values())
        assert total_prob == pytest.approx(1.0)

    def test_two_dice_known_probs(self):
        dist = dice_sum_distribution(2, 6)
        assert dist[2] == pytest.approx(1.0 / 36)
        assert dist[7] == pytest.approx(6.0 / 36)
        assert dist[12] == pytest.approx(1.0 / 36)

    def test_three_dice_total_probability(self):
        dist = dice_sum_distribution(3, 6)
        total_prob = sum(dist.values())
        assert total_prob == pytest.approx(1.0)

    def test_large_dice(self):
        dist = dice_sum_distribution(1, 100)
        for i in range(1, 101):
            assert dist[i] == pytest.approx(0.01)


class TestCumulativeDistribution:
    def test_single_die_cdf(self):
        dist = dice_sum_distribution(1, 6)
        cdf = cumulative_distribution(dist)
        assert cdf[6] == pytest.approx(1.0)
        assert cdf[3] == pytest.approx(0.5)

    def test_two_dice_cdf(self):
        dist = dice_sum_distribution(2, 6)
        cdf = cumulative_distribution(dist)
        assert cdf[12] == pytest.approx(1.0)
        # P(2d6 <= 7) = 21/36 = 7/12 ≈ 0.5833
        assert cdf[7] == pytest.approx(21.0 / 36)


class TestExpectedMaxOfK:
    def test_k_equals_one(self):
        dist = {1: 0.5, 2: 0.5}
        result = expected_max_of_k(dist, 1)
        assert result == pytest.approx(1.5)

    def test_k_equals_two_simple(self):
        dist = {1: 0.5, 2: 0.5}
        result = expected_max_of_k(dist, 2)
        # P(max=1) = 0.25, P(max=2) = 0.75
        # E = 1*0.25 + 2*0.75 = 1.75
        assert result == pytest.approx(1.75)

    def test_k_increases_expected_max(self):
        dist = dice_sum_distribution(3, 6)
        e1 = expected_max_of_k(dist, 1)
        e2 = expected_max_of_k(dist, 2)
        e5 = expected_max_of_k(dist, 5)
        e10 = expected_max_of_k(dist, 10)
        assert e1 < e2 < e5 < e10

    def test_k_equals_one_matches_expected_value(self):
        dist = dice_sum_distribution(3, 6)
        e_max = expected_max_of_k(dist, 1)
        e_direct = sum(v * p for v, p in dist.items())
        assert e_max == pytest.approx(e_direct)

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            expected_max_of_k({1: 1.0}, 0)


# =============================================================================
# Expected Sum of Top K Tests
# =============================================================================

class TestExpectedSumOfTopK:
    """Tests for expected_sum_of_top_k(dist, n, k)."""

    def test_k_equals_1_matches_max_of_k(self):
        """With k=1, expected_sum_of_top_k should match expected_max_of_k."""
        dist = dice_sum_distribution(3, 6)
        for n in [1, 2, 5, 10]:
            e_max = expected_max_of_k(dist, n)
            e_top = expected_sum_of_top_k(dist, n, 1)
            assert e_top == pytest.approx(e_max)

    def test_n_equals_k_1(self):
        """With n=k=1, result should equal the distribution's expected value."""
        dist = {1: 0.5, 2: 0.5}
        result = expected_sum_of_top_k(dist, 1, 1)
        expected = sum(v * p for v, p in dist.items())
        assert result == pytest.approx(expected)

    def test_n_equals_k(self):
        """With n=k, result should equal n times the distribution mean."""
        dist = dice_sum_distribution(2, 6)
        mean = sum(v * p for v, p in dist.items())
        for n in [2, 3, 5]:
            result = expected_sum_of_top_k(dist, n, n)
            assert result == pytest.approx(n * mean)

    def test_n_equals_k_binary(self):
        """Known binary distribution with n=k."""
        dist = {1: 0.5, 2: 0.5}
        result = expected_sum_of_top_k(dist, 2, 2)
        # Sum of 2 draws from {1:0.5, 2:0.5} = 2 * 1.5 = 3.0
        assert result == pytest.approx(3.0)

    def test_top_k_increases_with_k(self):
        """Given fixed n, larger k should give larger or equal expected sum."""
        dist = dice_sum_distribution(3, 6)
        prev = 0.0
        for k in [1, 2, 3, 4, 5]:
            result = expected_sum_of_top_k(dist, 10, k)
            assert result >= prev
            prev = result

    def test_top_k_increases_with_n(self):
        """Given fixed k, larger n should give larger or equal expected sum."""
        dist = dice_sum_distribution(3, 6)
        prev = expected_sum_of_top_k(dist, 1, 1)  # k=1, n=1
        for n in [2, 5, 10, 20]:
            result = expected_sum_of_top_k(dist, n, 1)  # top 1 of n
            assert result >= prev
            prev = result

    def test_two_dice_known(self):
        """Known values for 2d6: top 1 of 2 = expected max, top 2 of 2 = sum."""
        dist = dice_sum_distribution(2, 6)
        top1 = expected_max_of_k(dist, 2)
        result_top1 = expected_sum_of_top_k(dist, 2, 1)
        assert result_top1 == pytest.approx(top1)

        mean = sum(v * p for v, p in dist.items())
        result_top2 = expected_sum_of_top_k(dist, 2, 2)
        assert result_top2 == pytest.approx(2 * mean)

    def test_binary_distribution_top_1_of_3(self):
        """Binary dist: top 1 of 3 draws."""
        # Distribution: P(1)=0.5, P(2)=0.5
        # P(max <= 1) = 0.5^3 = 0.125
        # P(max = 1) = 0.125, P(max = 2) = 0.875
        # E[max] = 1*0.125 + 2*0.875 = 1.875
        dist = {1: 0.5, 2: 0.5}
        result = expected_sum_of_top_k(dist, 3, 1)
        assert result == pytest.approx(1.875)

    def test_binary_distribution_top_2_of_3(self):
        """Binary dist: sum of top 2 of 3 draws."""
        # Distribution: P(1)=0.5, P(2)=0.5
        # This is the sum of draws minus the minimum.
        # We can verify by computing expected sum of all 3 minus expected min.
        # Expected sum of 3 draws = 3 * 1.5 = 4.5
        # Expected min: P(min >= 2) = 0.5^3 = 0.125, P(min = 1) = 0.875, P(min = 2) = 0.125
        # E[min] = 1*0.875 + 2*0.125 = 1.125
        # E[sum of top 2] = 4.5 - 1.125 = 3.375
        dist = {1: 0.5, 2: 0.5}
        result = expected_sum_of_top_k(dist, 3, 2)
        assert result == pytest.approx(4.5 - 1.125)

    def test_binary_distribution_top_3_of_3(self):
        """Binary dist: n=k, sum of all 3 draws."""
        dist = {1: 0.5, 2: 0.5}
        result = expected_sum_of_top_k(dist, 3, 3)
        assert result == pytest.approx(4.5)

    def test_invalid_k_raises(self):
        """k < 1 should raise ValueError."""
        with pytest.raises(ValueError, match="k must be >= 1"):
            expected_sum_of_top_k({1: 1.0}, 5, 0)

    def test_n_less_than_k_raises(self):
        """n < k should raise ValueError."""
        with pytest.raises(ValueError, match="n.*must be >= k"):
            expected_sum_of_top_k({1: 1.0}, 2, 3)

    def test_empty_dist_raises(self):
        """Empty distribution should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            expected_sum_of_top_k({}, 3, 1)


class TestConvolveDistributions:
    def test_single_distribution(self):
        d6 = dice_sum_distribution(1, 6)
        result = convolve_distributions([d6])
        assert result == d6

    def test_two_d6(self):
        d6 = dice_sum_distribution(1, 6)
        result = convolve_distributions([d6, d6])
        direct = dice_sum_distribution(2, 6)
        for k in result:
            assert result[k] == pytest.approx(direct[k])

    def test_empty_list(self):
        result = convolve_distributions([])
        assert result == {0: 1.0}


# =============================================================================
# CoC Data Tests
# =============================================================================

class TestCoCData:
    def test_has_eight_characteristics(self):
        assert len(COC_CHARACTERISTICS) == 8

    def test_all_attributes_present(self):
        names = [c.name for c in COC_CHARACTERISTICS]
        expected = ["STR", "CON", "DEX", "POW", "APP", "SIZ", "INT", "EDU"]
        assert names == expected

    def test_correct_formulas(self):
        formulas = {c.name: c.formula for c in COC_CHARACTERISTICS}
        assert formulas["STR"] == "3d6"
        assert formulas["CON"] == "3d6"
        assert formulas["DEX"] == "3d6"
        assert formulas["POW"] == "3d6"
        assert formulas["APP"] == "3d6"
        assert formulas["SIZ"] == "2d6+6"
        assert formulas["INT"] == "2d6+6"
        assert formulas["EDU"] == "2d6+6"

    def test_correct_expected_values(self):
        ev = {c.name: expected_value(parse_notation(c.formula)) for c in COC_CHARACTERISTICS}
        assert ev["STR"] == 52.5
        assert ev["CON"] == 52.5
        assert ev["DEX"] == 52.5
        assert ev["POW"] == 52.5
        assert ev["APP"] == 52.5
        assert ev["SIZ"] == 65.0
        assert ev["INT"] == 65.0
        assert ev["EDU"] == 65.0

    def test_total_expected_value(self):
        total = sum(expected_value(parse_notation(c.formula)) for c in COC_CHARACTERISTICS)
        # 5 attributes × 3d6 (52.5) + 3 attributes × 2d6+6 (65.0) = 457.5
        assert total == pytest.approx(457.5)


# =============================================================================
# Comparator Tests
# =============================================================================

class TestCompareRollVsBuy:
    @property
    def _expected_total_raw(self) -> float:
        """Expected total for a single set of 8 attributes (raw characteristic points)."""
        return sum(expected_value(parse_notation(c.formula)) for c in COC_CHARACTERISTICS)

    def test_mode_full_set_k_equals_one_matches_ev(self):
        """With K=1, expected best set should equal the sum of single expected values."""
        budget = self._expected_total_raw
        result = compare_roll_vs_buy(budget, 1, "full_set")
        assert result.expected_best_total == pytest.approx(self._expected_total_raw, rel=1e-2)

    def test_more_attempts_increases_expected(self):
        """More attempts should always give a higher or equal expected best."""
        budget = self._expected_total_raw + 10.0
        r1 = compare_roll_vs_buy(budget, 1, "full_set")
        r2 = compare_roll_vs_buy(budget, 2, "full_set")
        r5 = compare_roll_vs_buy(budget, 5, "full_set")
        assert r1.expected_best_total <= r2.expected_best_total
        assert r2.expected_best_total <= r5.expected_best_total

    def test_full_set_more_attempts_increases(self):
        budget = self._expected_total_raw + 10.0
        r1 = compare_roll_vs_buy(budget, 1, "full_set")
        r2 = compare_roll_vs_buy(budget, 5, "full_set")
        assert r1.expected_best_total <= r2.expected_best_total

    def test_difference_positive_when_rolling_better(self):
        """With enough attempts, rolling should beat a very low budget."""
        result = compare_roll_vs_buy(70, 5, "full_set")
        assert result.difference > 0

    def test_difference_negative_when_buying_better(self):
        """With a very high budget and few attempts, buying should win."""
        result = compare_roll_vs_buy(750, 1, "full_set")
        assert result.difference < 0

    def test_recommendation_rolling(self):
        result = compare_roll_vs_buy(70, 5, "full_set")
        assert "beats" in result.recommendation.lower()

    def test_recommendation_buying(self):
        result = compare_roll_vs_buy(750, 1, "full_set")
        assert "beats" in result.recommendation.lower()

    def test_invalid_budget(self):
        with pytest.raises(ValueError):
            compare_roll_vs_buy(-1, 1, "full_set")

    def test_invalid_attempts(self):
        with pytest.raises(ValueError):
            compare_roll_vs_buy(470, 0, "full_set")

    def test_invalid_mode(self):
        with pytest.raises(ValueError):
            compare_roll_vs_buy(470, 1, "invalid_mode")

    def test_mode_full_set_has_no_attributes(self):
        result = compare_roll_vs_buy(470, 3, "full_set")
        assert len(result.attributes) == 0

    def test_single_set_expected_in_full_mode(self):
        result = compare_roll_vs_buy(self._expected_total_raw, 3, "full_set")
        assert result.single_set_expected is not None
        assert result.single_set_expected == pytest.approx(self._expected_total_raw, rel=1e-2)

    def test_valid_modes_accepted(self):
        """Both 'full_set' and 'per_group' should be accepted."""
        budget = self._expected_total_raw
        r1 = compare_roll_vs_buy(budget, 1, "full_set")
        assert r1.mode == "full_set"
        r2 = compare_roll_vs_buy(budget, 1, "per_group")
        assert r2.mode == "per_group"


class TestComparePerGroupMode:
    """Tests for Mode B (per_group) comparison."""

    @property
    def _expected_total_raw(self) -> float:
        """Expected total for a single set of 8 attributes (raw characteristic points)."""
        return sum(expected_value(parse_notation(c.formula)) for c in COC_CHARACTERISTICS)

    def test_k_equals_1_matches_expected_value(self):
        """With X=1, per-group picks all rolls (top 5 of 5, top 3 of 3).
        So expected total should = single set expected total.
        """
        budget = self._expected_total_raw
        result = compare_roll_vs_buy(budget, 1, "per_group")
        # Top 5 of 5 = sum of all five 3d6 rolls
        # Top 3 of 3 = sum of all three 2d6+6 rolls
        assert result.expected_best_total == pytest.approx(self._expected_total_raw, rel=1e-2)

    def test_more_attempts_increases_expected(self):
        """More attempts should give higher or equal expected best total."""
        budget = self._expected_total_raw + 10.0
        r1 = compare_roll_vs_buy(budget, 1, "per_group")
        r2 = compare_roll_vs_buy(budget, 2, "per_group")
        r5 = compare_roll_vs_buy(budget, 5, "per_group")
        assert r1.expected_best_total <= r2.expected_best_total
        assert r2.expected_best_total <= r5.expected_best_total

    def test_per_group_vs_full_set(self):
        """For the same X, Mode B should always give >= expected total than Mode A,
        because Mode B has more selection freedom.
        """
        r_full = compare_roll_vs_buy(500, 3, "full_set")
        r_group = compare_roll_vs_buy(500, 3, "per_group")
        assert r_group.expected_best_total >= r_full.expected_best_total

    def test_difference_positive_when_rolling_better(self):
        """With enough attempts, Mode B rolling should beat a low budget."""
        result = compare_roll_vs_buy(70, 5, "per_group")
        assert result.difference > 0

    def test_difference_negative_when_buying_better(self):
        """With a very high budget and few attempts, buying should still win."""
        result = compare_roll_vs_buy(750, 1, "per_group")
        assert result.difference < 0

    def test_group_fields_populated(self):
        """Per-group specific fields should be populated."""
        result = compare_roll_vs_buy(500, 3, "per_group")
        assert result.group_3d6_expected_best is not None
        assert result.group_2d6_expected_best is not None
        assert result.group_3d6_pool_size is not None
        assert result.group_2d6_pool_size is not None
        assert result.group_3d6_pool_size == 15  # 5 × 3
        assert result.group_2d6_pool_size == 9   # 3 × 3

    def test_group_fields_empty_in_full_mode(self):
        """Per-group fields should be None in full_set mode."""
        result = compare_roll_vs_buy(500, 3, "full_set")
        assert result.group_3d6_expected_best is None
        assert result.group_2d6_expected_best is None
        assert result.group_3d6_pool_size is None
        assert result.group_2d6_pool_size is None

    def test_recommendation_rolling(self):
        result = compare_roll_vs_buy(70, 5, "per_group")
        assert "beats" in result.recommendation.lower()

    def test_recommendation_buying(self):
        result = compare_roll_vs_buy(750, 1, "per_group")
        assert "beats" in result.recommendation.lower()

    def test_single_set_expected_in_per_group_mode(self):
        """single_set_expected should still be populated in per_group mode."""
        result = compare_roll_vs_buy(self._expected_total_raw, 3, "per_group")
        assert result.single_set_expected is not None
        assert result.single_set_expected == pytest.approx(self._expected_total_raw, rel=1e-2)

    def test_group_3d6_expected_in_range(self):
        """Best 3d6 sum should be between min_possible and max_possible (×5 percentile)."""
        result = compare_roll_vs_buy(500, 5, "per_group")
        best_3d6 = result.group_3d6_expected_best or 0.0
        # 3d6 ranges from 3 to 18. Best 5: at least 5×3=15, at most 5×18=90
        # After ×5: at least 75, at most 450
        assert 75.0 <= best_3d6 <= 450.0

    def test_group_2d6_expected_in_range(self):
        """Best 2d6+6 sum should be between min_possible and max_possible (×5 percentile)."""
        result = compare_roll_vs_buy(500, 5, "per_group")
        best_2d6 = result.group_2d6_expected_best or 0.0
        # 2d6+6 ranges from 8 to 18. Best 3: at least 3×8=24, at most 3×18=54
        # After ×5: at least 120, at most 270
        assert 120.0 <= best_2d6 <= 270.0
