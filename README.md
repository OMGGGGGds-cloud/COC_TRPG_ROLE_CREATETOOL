# TRPG Assistant — Expected Value Calculator

A Python tool for analyzing dice probabilities in Call of Cthulhu 7th Edition. Provides exact theoretical expected values using probability math — no random simulation.
It is fully coded by LLM.
## Features

### 1. Expected Value Calculator
Calculate the theoretical expected percentile value (×5) for any dice notation:

| Notation | Formula | Expected Value (×5) |
|----------|---------|---------------------|
| `3d6`    | 3 × (6+1)/2 × 5 | 52.5 |
| `2d6+6`  | (2 × (6+1)/2 + 6) × 5 | 65.0 |
| `5d6`    | 5 × (6+1)/2 × 5 | 87.5 |
| `1d20`   | 1 × (20+1)/2 × 5 | 52.5 |
| `4d4-2`  | (4 × (4+1)/2 - 2) × 5 | 40.0 |

### 2. CoC 7e Character Creation Reference
Displays all 8 characteristics with their standard dice formulas and expected percentile values (raw score ×5):

| Attribute | Formula | Expected (×5) |
|-----------|---------|---------------|
| STR       | 3d6     | 52.5          |
| CON       | 3d6     | 52.5          |
| DEX       | 3d6     | 52.5          |
| POW       | 3d6     | 52.5          |
| APP       | 3d6     | 52.5          |
| SIZ       | 2d6+6   | 65.0          |
| INT       | 2d6+6   | 65.0          |
| EDU       | 2d6+6   | 65.0          |
| **Total** |         | **457.5**     |

### 3. Roll vs. Point-Buy Comparison
Compare rolling dice (with multiple attempts) against a point-buy budget — helps answer "is it better to roll X times and pick the best, or just take X points?"

Two comparison modes are available:

**Mode A: Best of K Full Sets** — Roll X complete attribute sets and pick the set with the highest total sum. Shows expected best total vs. budget. This is the constrained approach: you must take all attributes from the same set.

**Mode B: Best per Formula Group** — Roll X complete attribute sets, then:
- **Pool** all 3d6-type rolls (5 per set × X sets = 5X total rolls), pick the **best 5**
- **Pool** all 2d6+6-type rolls (3 per set × X sets = 3X total rolls), pick the **best 3**
- Sum the 8 selected characteristic values for the final total

This gives more selection freedom than Mode A, since you independently optimize within each formula group.

All calculations use **exact order statistics** on full probability distributions — no random simulation.

## Installation

1. Ensure Python 3.8+ is installed.
2. No external dependencies required (standard library only).
3. Run: `python main.py`

## Usage

```
===== TRPG Expected Value Calculator =====
1. Calculate expected value for a dice formula
2. CoC 7e Character Creation Reference
3. Roll vs Point-Buy Comparison
4. Exit
===========================================
```

### Example: Expected Value
```
Enter dice notation: 5d6
Formula: 5d6
Expected percentile value: 87.5
  (17.5 per die (×5) × 5 dice)
```

### Example: Roll vs. Buy Comparison — Mode A (Full Set)
```
Point-buy budget: 450
Number of attempts (X): 5
Select mode (1-2): 1

Mode: Mode A — Best of K Full Sets

Expected total (single set):     457.5
Expected best total (K=5):       503.1

Expected best total: 503.1
Point-buy budget:    450.0
Difference:           +53.1

Recommendation: Rolling beats buying by 53.1 points. With 5 attempt(s), rolling yields a better expected outcome.
```

### Example: Roll vs. Buy Comparison — Mode B (Per Group)
```
Point-buy budget: 450
Number of attempts (X): 3
Select mode (1-2): 2

Mode: Mode B — Best per Formula Group

Pool: 5 × 3d6-type across 3 set(s) → 15 rolls, pick best 5
Pool: 3 × 2d6+6-type across 3 set(s) → 9 rolls, pick best 3

Expected best 3d6 total (top 5 of 15):    339.3
Expected best 2d6+6 total (top 3 of 9):   231.4
──────────────────────────────────────────────────
Expected best total (sum):                  570.7

Expected best total: 570.7
Point-buy budget:     450.0
Difference:           +120.7

Recommendation: Rolling beats buying by 120.7 points. With 3 attempt(s), rolling yields a better expected outcome.
```

## Running Tests

```bash
python -m pytest tests/test_dice_calc.py -v
```

## Project Structure

```
TRPG/
├── main.py                    # Entry point
├── dice_calc/
│   ├── __init__.py            # Package init
│   ├── parser.py              # Dice notation parser
│   ├── calculator.py          # Expected value formulas
│   ├── distribution.py        # Probability distributions & order statistics
│   ├── coc_data.py            # CoC 7e characteristic definitions
│   ├── comparator.py          # Roll vs point-buy comparison (Mode A & B)
│   └── cli.py                 # CLI interface
├── tests/
│   └── test_dice_calc.py      # Unit tests
└── README.md                  # This file
```

## How It Works

The tool uses **exact probability math** rather than random simulation:

1. **Dice sum distribution:** Computed via dynamic programming (convolution) — enumerates all possible sums of NdX with their exact probabilities.
2. **Order statistics:** `E[max of K draws]` is computed from `P(max ≤ x) = P(single ≤ x)^K`.
3. **Convolution:** Independent attribute distributions are combined to get the distribution of total character sum.

No `random` module is used — results are deterministic and mathematically exact.
