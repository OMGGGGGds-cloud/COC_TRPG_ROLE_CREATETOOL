"""CLI interface for the TRPG Expected Value Calculator."""

from dice_calc.calculator import expected_value_str, expected_value
from dice_calc.coc_data import COC_CHARACTERISTICS
from dice_calc.comparator import compare_roll_vs_buy
from dice_calc.parser import parse_notation


def _print_header(title: str) -> None:
    """Print a formatted header."""
    width = 55
    print()
    print("=" * width)
    print(f" {title}")
    print("=" * width)


def _print_menu() -> None:
    """Print the main menu."""
    print()
    print("===== TRPG Expected Value Calculator =====")
    print("1. Calculate expected value for a dice formula")
    print("2. CoC 7e Character Creation Reference")
    print("3. Roll vs Point-Buy Comparison")
    print("4. Exit")
    print("===========================================")


def _option_expected_value() -> None:
    """Menu option 1: Calculate expected value."""
    _print_header("Expected Value Calculator")
    while True:
        print()
        notation = input("Enter dice notation (or 'back' to return): ").strip()
        if notation.lower() in ("back", "b", "exit"):
            break
        if not notation:
            continue
        try:
            result = expected_value_str(notation)
            print()
            print(result)
        except ValueError as e:
            print(f"  Error: {e}")


def _option_coc_reference() -> None:
    """Menu option 2: Show CoC 7e character creation reference."""
    _print_header("CoC 7e Character Creation Reference")

    print()
    print(f"{'Attribute':<10} {'Formula':<15} {'Expected':<12} {'Full Name':<20}")
    print("-" * 60)
    total_expected = 0.0
    for char in COC_CHARACTERISTICS:
        ev = expected_value(parse_notation(char.formula))
        total_expected += ev
        print(f"{char.name:<10} {char.formula:<15} {ev:<12.1f} {char.full_name:<20}")

    print("-" * 60)
    print(f"{'Total':<10} {'':<15} {total_expected:<12.1f} {'(sum of all 8)':<20}")
    print(f"{'Average':<10} {'':<15} {total_expected / 8:<12.1f} {'(per attribute)':<20}")
    print()


def _option_roll_vs_buy() -> None:
    """Menu option 3: Roll vs Point-Buy comparison."""
    _print_header("Roll vs Point-Buy Comparison")

    # Get budget
    while True:
        try:
            budget_str = input("Point-buy budget (total points available): ").strip()
            if budget_str.lower() in ("back", "b", "exit"):
                return
            budget = float(budget_str)
            if budget < 0:
                print("  Budget cannot be negative.")
                continue
            break
        except ValueError:
            print("  Please enter a valid number.")

    # Get number of attempts
    while True:
        try:
            attempts_str = input("Number of attempts (X): ").strip()
            if attempts_str.lower() in ("back", "b", "exit"):
                return
            attempts = int(attempts_str)
            if attempts < 1:
                print("  Attempts must be at least 1.")
                continue
            break
        except ValueError:
            print("  Please enter a valid integer.")

    # Select mode
    print()
    print("  Comparison modes:")
    print("    1. Best of K Full Sets (Mode A)")
    print("       - Roll complete sets, pick the best set by total sum")
    print("    2. Best per Formula Group (Mode B)")
    print("       - Pool rolls by formula (3d6 vs 2d6+6), pick best within each group")
    print()
    while True:
        mode_choice = input("Select mode (1-2): ").strip()
        if mode_choice.lower() in ("back", "b", "exit"):
            return
        if mode_choice == "1":
            mode_key = "full_set"
            break
        elif mode_choice == "2":
            mode_key = "per_group"
            break
        else:
            print("  Please enter 1 or 2.")

    # Run comparison
    try:
        result = compare_roll_vs_buy(budget, attempts, mode_key)
    except ValueError as e:
        print(f"  Error: {e}")
        return

    # Display results
    print()
    print(f"Point-buy budget: {result.point_buy_budget:.1f} points")
    print(f"Attempts (X):      {result.attempts}")
    print(f"Mode:              {'Mode A - Best of K Full Sets' if result.mode == 'full_set' else 'Mode B - Best per Formula Group'}")
    print()

    if result.mode == "full_set":
        # Mode A: Full-set summary
        single_expected = result.single_set_expected or 0.0
        print(f"Expected total (single set):     {single_expected:.1f}")
        print(f"Expected best total (K={result.attempts}): {result.expected_best_total:.1f}")
    else:
        # Mode B: Per-group summary
        single_expected = result.single_set_expected or 0.0
        pool_3d6 = result.group_3d6_pool_size or 0
        pool_2d6 = result.group_2d6_pool_size or 0
        best_3d6 = result.group_3d6_expected_best or 0.0
        best_2d6 = result.group_2d6_expected_best or 0.0
        print(f"Pool: 5 x 3d6-type across {result.attempts} set(s) -> {pool_3d6} rolls, pick best 5")
        print(f"Pool: 3 x 2d6+6-type across {result.attempts} set(s) -> {pool_2d6} rolls, pick best 3")
        print()
        print(f"Expected best 3d6 total (top 5 of {pool_3d6}):    {best_3d6:.1f}")
        print(f"Expected best 2d6+6 total (top 3 of {pool_2d6}):  {best_2d6:.1f}")
        print(f"{'-' * 50}")
        print(f"Expected best total (sum):                   {result.expected_best_total:.1f}")

    print()
    print(f"Expected best total: {result.expected_best_total:.1f}")
    print(f"Point-buy budget:    {result.point_buy_total:.1f}")
    print(f"Difference:          {result.difference:+.1f}")
    print()
    print(f"Recommendation: {result.recommendation}")
    print()


def run_cli() -> None:
    """Run the main CLI loop."""
    print("Welcome to the TRPG Expected Value Calculator!")
    print("This tool helps analyze dice probabilities for Call of Cthulhu 7e.")

    while True:
        _print_menu()
        choice = input("Select option (1-4): ").strip()

        if choice == "1":
            _option_expected_value()
        elif choice == "2":
            _option_coc_reference()
        elif choice == "3":
            _option_roll_vs_buy()
        elif choice == "4":
            print()
            print("Goodbye!")
            break
        else:
            print("  Invalid option. Please enter 1-4.")
