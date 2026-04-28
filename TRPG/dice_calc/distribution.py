"""Probability distributions for sums of dice and order statistics.

Provides exact computation of the probability distribution for the sum of
rolled dice using dynamic programming (convolution). Also provides order
statistics to compute the expected maximum of K independent draws and the
expected sum of the top K out of N draws.

No random number generation is used — all results are exact probabilities.
"""

import math
from typing import Dict


def dice_sum_distribution(count: int, sides: int) -> Dict[int, float]:
    """Compute the exact probability distribution for the sum of NdX.

    Uses dynamic programming to enumerate all possible sums and their
    probabilities without iterating over individual die outcomes.

    Args:
        count: Number of dice (must be >= 1).
        sides: Number of sides per die (must be >= 2).

    Returns:
        A dict mapping {sum_value: probability} where probabilities
        sum to 1.0 (within floating-point precision).

    Example:
        >>> dist = dice_sum_distribution(2, 6)
        >>> dist[2]   # 1/36
        0.027777777777777776
        >>> dist[7]   # 6/36
        0.16666666666666666
    """
    # Start with one die: uniform distribution over 1..sides
    dist: Dict[int, float] = {i: 1.0 / sides for i in range(1, sides + 1)}

    # Convolve additional dice
    for _ in range(count - 1):
        new_dist: Dict[int, float] = {}
        for existing_sum, existing_prob in dist.items():
            for face in range(1, sides + 1):
                new_sum = existing_sum + face
                new_dist[new_sum] = new_dist.get(new_sum, 0.0) + existing_prob * (1.0 / sides)
        dist = new_dist

    return dist


def dice_sum_distribution_with_modifier(
    count: int, sides: int, modifier: int = 0
) -> Dict[int, float]:
    """Like dice_sum_distribution but adds a flat modifier to all outcomes."""
    base = dice_sum_distribution(count, sides)
    if modifier == 0:
        return base
    return {k + modifier: v for k, v in base.items()}


def cumulative_distribution(dist: Dict[int, float]) -> Dict[int, float]:
    """Convert a probability mass function to a cumulative distribution function.

    Returns a dict mapping each value to P(X <= value).
    """
    sorted_vals = sorted(dist.keys())
    cdf: Dict[int, float] = {}
    cumulative = 0.0
    for v in sorted_vals:
        cumulative += dist[v]
        cdf[v] = cumulative
    return cdf


def expected_max_of_k(dist: Dict[int, float], k: int) -> float:
    """Compute the expected maximum of K independent draws from a distribution.

    Uses order statistics: P(max <= x) = P(X <= x)^K
    Then: E[max] = sum over x of x * P(max = x)

    Args:
        dist: The probability distribution (PMF) as {value: probability}.
        k: Number of independent draws (must be >= 1).

    Returns:
        The expected maximum value.

    Example:
        >>> dist = {1: 0.5, 2: 0.5}  # fair coin flip values 1 or 2
        >>> expected_max_of_k(dist, 1)
        1.5
        >>> expected_max_of_k(dist, 2)
        1.75
    """
    if k < 1:
        raise ValueError(f"Number of attempts must be at least 1, got {k}.")

    cdf = cumulative_distribution(dist)
    sorted_vals = sorted(dist.keys())

    # For k=1, expected max = expected value of the distribution
    if k == 1:
        return sum(v * dist[v] for v in sorted_vals)

    # P(max <= x) = P(X <= x)^k
    max_cdf = {x: prob ** k for x, prob in cdf.items()}

    # P(max = x) = P(max <= x) - P(max <= x-1)
    expected = 0.0
    prev_cdf = 0.0
    for x in sorted_vals:
        p_max_eq_x = max_cdf[x] - prev_cdf
        expected += x * p_max_eq_x
        prev_cdf = max_cdf[x]

    return expected


def expected_sum_of_top_k(dist: Dict[int, float], n: int, k: int) -> float:
    """Compute the expected sum of the top K out of N independent draws.

    Uses order statistics: for each position j (j-th smallest out of n),
    P(X_(j) <= x) = sum_{i=j}^{n} C(n,i) * F(x)^i * (1-F(x))^(n-i)
    where F is the CDF of the distribution.

    The top K sum = sum_{j=n-k+1}^{n} E[X_(j)]

    Args:
        dist: The probability distribution (PMF) as {value: probability}.
        n: Total number of independent draws (must be >= k).
        k: Number of top items to sum (must be >= 1).

    Returns:
        The expected sum of the top k values.

    Raises:
        ValueError: If n < k, k < 1, or dist is empty.

    Example:
        >>> dist = {1: 0.5, 2: 0.5}
        >>> expected_sum_of_top_k(dist, 2, 1)
        1.75
        >>> expected_sum_of_top_k(dist, 2, 2)
        3.0  # sum of both draws = 2 * 1.5 = 3.0
    """
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}.")
    if n < k:
        raise ValueError(f"n ({n}) must be >= k ({k}).")
    if not dist:
        raise ValueError("Distribution cannot be empty.")

    # When k == 1, delegate to the existing optimized implementation
    if k == 1:
        return expected_max_of_k(dist, n)

    # When n == k, we always take all draws: expected sum = n * mean
    if n == k:
        mean = sum(v * p for v, p in dist.items())
        return n * mean

    # Build the CDF: F(x) = P(X <= x)
    sorted_vals = sorted(dist.keys())
    cdf = cumulative_distribution(dist)

    # Compute P(max <= x) = F(x)^n for all x (used in edge calculations)
    # For the j-th order statistic: P(X_(j) <= x) = sum_{i=j}^{n} C(n,i) * F(x)^i * (1-F(x))^(n-i)

    expected_sum = 0.0

    # We need E[X_(j)] for j = n-k+1, ..., n (the top k order statistics)
    for order_j in range(n - k + 1, n + 1):
        prev_cdf_val = 0.0
        order_expected = 0.0
        for v in sorted_vals:
            f_x = cdf[v]
            # P(X_(j) <= v) = sum_{i=order_j}^{n} C(n,i) * F(v)^i * (1-F(v))^(n-i)
            cdf_at_v = 0.0

            # Optimization: if f_x == 0, then F(v)^i = 0 for all i > 0
            # and (1-F(v))^(n-i) = 1^{n-i} = 1
            if f_x == 0.0:
                if order_j == 0:
                    cdf_at_v = 1.0
                else:
                    cdf_at_v = 0.0
            elif f_x == 1.0:
                # F(v) = 1 means all draws are <= v
                cdf_at_v = 1.0
            else:
                for i in range(order_j, n + 1):
                    cdf_at_v += (
                        math.comb(n, i)
                        * (f_x ** i)
                        * ((1.0 - f_x) ** (n - i))
                    )

            # P(X_(j) = v) = P(X_(j) <= v) - P(X_(j) <= v-1)
            p_eq_v = cdf_at_v - prev_cdf_val
            if p_eq_v > 0:
                order_expected += v * p_eq_v
            prev_cdf_val = cdf_at_v

        expected_sum += order_expected

    return expected_sum


def convolve_distributions(
    dists: list[Dict[int, float]]
) -> Dict[int, float]:
    """Convolve multiple independent probability distributions.

    Given distributions for independent random variables X1, X2, ..., Xn,
    computes the distribution of X1 + X2 + ... + Xn.

    Args:
        dists: List of probability distributions (PMFs) as {value: probability}.

    Returns:
        The convolved distribution as {sum_value: probability}.

    Example:
        >>> d6 = dice_sum_distribution(1, 6)
        >>> sum_2d6 = convolve_distributions([d6, d6])
        >>> sum_2d6[7]
        0.16666666666666666
    """
    if not dists:
        return {0: 1.0}

    result = dists[0]
    for dist in dists[1:]:
        new_result: Dict[int, float] = {}
        for val1, prob1 in result.items():
            for val2, prob2 in dist.items():
                new_val = val1 + val2
                new_result[new_val] = new_result.get(new_val, 0.0) + prob1 * prob2
        result = new_result

    return result
