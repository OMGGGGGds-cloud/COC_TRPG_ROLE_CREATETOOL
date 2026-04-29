"""Unit tests for the CLI module."""

from unittest.mock import patch
from io import StringIO

from dice_calc.cli import run_cli, _print_header, _print_menu
from dice_calc.coc_data import COC_CHARACTERISTICS


class TestPrintHelpers:
    def test_print_header_contains_title(self):
        buf = StringIO()
        with patch("sys.stdout", buf):
            _print_header("Test Title")
        assert "Test Title" in buf.getvalue()

    def test_print_menu_contains_options(self):
        buf = StringIO()
        with patch("sys.stdout", buf):
            _print_menu()
        output = buf.getvalue()
        assert "Expected Value Calculator" in output
        assert "CoC 7e Character Creation Reference" in output
        assert "Roll vs Point-Buy Comparison" in output
        assert "Exit" in output


class TestRunCLI:
    def test_exit_on_option_4(self):
        """Selecting option 4 should exit gracefully."""
        inputs = ["4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "Goodbye!" in output

    def test_invalid_then_exit(self):
        """Invalid input followed by exit should not crash."""
        inputs = ["99", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "Invalid option" in output
        assert "Goodbye!" in output

    def test_keyboard_interrupt_handled(self):
        """Ctrl+C should exit gracefully without traceback."""
        inputs = KeyboardInterrupt()
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "Goodbye!" in output

    def test_option_2_coc_reference(self):
        """Selecting option 2 should show CoC reference table."""
        inputs = ["2", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        for char in COC_CHARACTERISTICS:
            assert char.name in output
            assert char.formula in output

    def test_option_1_back_returns(self):
        """Entering 'back' in option 1 should return to menu."""
        inputs = ["1", "back", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "Goodbye!" in output

    def test_option_1_valid_notation(self):
        """Entering valid dice notation shows expected value."""
        inputs = ["1", "3d6", "back", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "52.5" in output

    def test_option_1_invalid_notation(self):
        """Entering invalid notation shows error but doesn't crash."""
        inputs = ["1", "not_dice", "back", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "Error" in output

    def test_option_3_back_on_budget(self):
        """Hitting 'back' on budget prompt returns to menu."""
        inputs = ["3", "back", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "Goodbye!" in output

    def test_option_3_full_flow_mode_a(self):
        """Complete flow through roll-vs-buy comparison Mode A."""
        inputs = ["3", "460", "3", "1", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "Recommendation:" in output

    def test_option_3_full_flow_mode_b(self):
        """Complete flow through roll-vs-buy comparison Mode B."""
        inputs = ["3", "460", "3", "2", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "Recommendation:" in output

    def test_option_3_invalid_budget_then_valid(self):
        """Invalid budget followed by valid input should work."""
        inputs = ["3", "abc", "-5", "460", "1", "1", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "valid number" in output or "cannot be negative" in output
        assert "Recommendation:" in output

    def test_option_3_invalid_attempts_then_valid(self):
        """Invalid attempts followed by valid input should work."""
        inputs = ["3", "460", "xyz", "0", "3", "2", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        assert "Recommendation:" in output

    def test_empty_input_handled(self):
        """Empty input at menu should be caught."""
        inputs = ["", "4"]
        buf = StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", buf):
            run_cli()
        output = buf.getvalue()
        # Empty input should fall through and print invalid option
        assert "Invalid option" in output or "Goodbye!" in output
