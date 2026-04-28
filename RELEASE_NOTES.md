# Release Notes — `trpg-assistant` v1.0.0

**Date:** 2026-04-28  
**Project:** [`trpg-assistant`](pyproject.toml:6) — TRPG dice probability calculator for Call of Cthulhu 7th Edition  
**License:** [MIT](LICENSE)

---

## Overview

`trpg-assistant` v1.0.0 is the initial public release. It provides mathematically exact (non-simulated) dice probability analysis for Call of Cthulhu 7th Edition character creation, including expected value calculation, a character creation reference, and a roll-vs-point-buy comparison engine.

All calculations use **exact probability math** (dynamic programming convolutions and order statistics) — no random number generation is used.

---

## Features

### 1. Dice Notation Parser ([`dice_calc/parser.py`](dice_calc/parser.py))
- Parses standard dice notation: `NdX`, `NdX+Y`, `NdX-Y`
- Supports arbitrary die counts and sides (validated: `count >= 1`, `sides >= 2`)
- Case-insensitive and whitespace-tolerant input
- Returns a [`DiceExpression`](dice_calc/parser.py:12) dataclass with `count`, `sides`, and `modifier` fields

### 2. Expected Value Calculator ([`dice_calc/calculator.py`](dice_calc/calculator.py))
- Computes the theoretical expected percentile value (×5 for CoC 7e) for any dice formula
- Formula: `E[NdX+Y] = N × (X+1)/2 + Y` (raw score), then ×5 for percentile
- Handles both positive and negative flat modifiers
- Formatted output with per-die and per-modifier breakdown

| Notation | Formula | Expected Value (×5) |
|----------|---------|---------------------|
| `3d6`    | 3 × (6+1)/2 × 5       | 52.5 |
| `2d6+6`  | (2 × (6+1)/2 + 6) × 5 | 65.0 |
| `5d6`    | 5 × (6+1)/2 × 5       | 87.5 |
| `1d20`   | 1 × (20+1)/2 × 5      | 52.5 |
| `4d4-2`  | (4 × (4+1)/2 - 2) × 5 | 40.0 |

### 3. CoC 7e Character Creation Reference ([`dice_calc/coc_data.py`](dice_calc/coc_data.py))
- All 8 standard CoC 7th Edition characteristics with their dice formulas

| Attribute | Formula | Expected (×5) | Full Name |
|-----------|---------|---------------|-----------|
| STR       | 3d6     | 52.5          | Strength |
| CON       | 3d6     | 52.5          | Constitution |
| DEX       | 3d6     | 52.5          | Dexterity |
| POW       | 3d6     | 52.5          | Power |
| APP       | 3d6     | 52.5          | Appearance |
| SIZ       | 2d6+6   | 65.0          | Size |
| INT       | 2d6+6   | 65.0          | Intelligence |
| EDU       | 2d6+6   | 65.0          | Education |
| **Total** |         | **457.5**     | |

### 4. Roll vs. Point-Buy Comparison ([`dice_calc/comparator.py`](dice_calc/comparator.py))

Two comparison modes are available, both using exact order statistics:

- **Mode A — Best of K Full Sets:** Roll K complete 8-attribute sets and pick the set with the highest total sum. Computed via full distribution convolution (all 8 characteristics) plus order statistics for the expected maximum of K draws.

- **Mode B — Best per Formula Group:** Roll K complete sets, then:
  - Pool all 3d6-type rolls (5 per set × K sets = 5K total), pick the best 5
  - Pool all 2d6+6-type rolls (3 per set × K sets = 3K total), pick the best 3
  - Sum the 8 selected values for the final total
  - Provides more selection freedom than Mode A

### 5. Probability Distribution Engine ([`dice_calc/distribution.py`](dice_calc/distribution.py))
- **`dice_sum_distribution(count, sides)`:** Exact PMF of NdX via dynamic programming (convolution)
- **`cumulative_distribution(dist)`:** Converts PMF to CDF
- **`expected_max_of_k(dist, k)`:** Order statistics — expected maximum of K independent draws
- **`expected_sum_of_top_k(dist, n, k)`:** Expected sum of the top K out of N draws using binomial-order-statistics formulas
- **`convolve_distributions(dists)`:** Convolves independent PMFs into a joint sum distribution

### 6. Interactive CLI ([`dice_calc/cli.py`](dice_calc/cli.py))
- Menu-driven interface with 4 options:
  1. Calculate expected value for a dice formula
  2. CoC 7e Character Creation Reference
  3. Roll vs Point-Buy Comparison
  4. Exit
- Entry point: [`main.py`](main.py) or `trpg` console script (registered in [`pyproject.toml`](pyproject.toml:33))

### 7. PyInstaller Build Support
- [`trpg-calc.spec`](trpg-calc.spec) with optimized exclusion of unused standard library modules (GUI frameworks, async, email, multimedia, compression, etc.)
- Builds a single `trpg-calc.exe` console binary

---

## Installation

```bash
# Via pip (source distribution)
pip install trpg-assistant

# Direct execution
python main.py

# Or use the installed console script
trpg
```

**Requirements:** Python 3.8+ (standard library only — no external dependencies).

---

## Package Structure

```
dice_calc/
├── __init__.py        — Public API exports
├── parser.py          — Dice notation parsing (NdX, NdX+Y)
├── calculator.py      — Expected value computation (×5 percentile)
├── distribution.py    — Exact probability distributions & order statistics
├── coc_data.py        — CoC 7e characteristic definitions
├── comparator.py      — Roll vs. point-buy (Mode A & B)
└── cli.py             — Interactive CLI menu
tests/
└── test_dice_calc.py  — 54+ unit tests
```

---

## Testing

The test suite covers all modules thoroughly:

| Module | Tests | Coverage Highlights |
|--------|-------|---------------------|
| Parser | 15    | Valid notation, modifiers, edge cases, error handling |
| Calculator | 8 | Expected values for all formula types |
| Distribution | 8 | PMF correctness, CDF, max-of-k |
| Expected Sum of Top K | 14 | Correctness, monotonicity, boundaries |
| Convolution | 3 | Single/two distributions, empty input |
| CoC Data | 5 | Attributes, formulas, expected values |
| Comparator Mode A | 11 | Monotonicity, recommendations, validation |
| Comparator Mode B | 12 | Per-group fields, ranges, monotonicity |

```bash
python -m pytest tests/test_dice_calc.py -v
```

---

## Known Limitations

- CLI-only interface (no GUI)
- Flat modifiers are scaled by ×5 alongside dice values (matches CoC 7e convention)
- No support for advanced dice notation features (e.g., `d%`, `dF`, rerolls, exploding dice)
- Distribution engine uses exact enumeration — very large dice counts (e.g., 1000d6) may be computationally expensive

---

## Acknowledgments

- Built for the Call of Cthulhu 7th Edition role-playing game by Chaosium
- Uses no external dependencies — standard library only
