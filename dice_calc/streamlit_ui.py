"""Streamlit web UI for the TRPG Expected Value Calculator."""

import streamlit as st
from dice_calc.calculator import expected_value_str, expected_value, COC_PERCENTILE_MULTIPLIER
from dice_calc.coc_data import COC_CHARACTERISTICS
from dice_calc.comparator import compare_roll_vs_buy
from dice_calc.parser import parse_notation


def run_web():
    """Launch the Streamlit web UI."""
    import sys
    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())


# ---- Only executed when run via `streamlit run` ----
st.set_page_config(page_title="TRPG Assistant", page_icon="🎲", layout="wide")

st.title("🎲 TRPG Assistant")
st.caption("Expected Value Calculator for Call of Cthulhu 7th Edition")
st.caption("Fully coded by LLM — exact probability math, no random simulation.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select a tool",
        ["Expected Value", "CoC 7e Reference", "Roll vs Point-Buy"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("### About")
    st.markdown(
        "This tool analyzes dice probabilities for CoC 7e character creation "
        "using **exact probability math** — no random number generation."
    )
    st.caption(
        "GitHub: [COC_TRPG_ROLE_CREATETOOL]"
        "(https://github.com/OMGGGGGds-cloud/COC_TRPG_ROLE_CREATETOOL)"
    )

# =====================================================================
# Page 1: Expected Value Calculator
# =====================================================================
if page == "Expected Value":
    st.header("Expected Value Calculator")
    st.markdown("Enter a dice notation to see the expected value.")

    col1, col2 = st.columns([3, 1])
    with col1:
        notation = st.text_input(
            "Dice notation",
            placeholder="e.g. 3d6, 2d6+6, 5d6, 1d20, 4d4-2",
            label_visibility="collapsed",
        )
    with col2:
        calculate = st.button("Calculate", use_container_width=True)

    if calculate and notation.strip():
        try:
            result = expected_value_str(notation.strip())
            expr = parse_notation(notation.strip())
            total = expected_value(expr)

            st.divider()

            raw_expected = total / COC_PERCENTILE_MULTIPLIER

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Formula", expr.notation)
            with col_b:
                st.metric("Expected Value", f"{raw_expected:g}")

            with st.expander("Breakdown", expanded=True):
                per_die = (expr.sides + 1) / 2.0
                st.markdown(f"- **Per-die expected:** {(per_die):g}")
                st.markdown(f"- **Dice count:** {expr.count}")
                if expr.modifier:
                    st.markdown(f"- **Flat modifier:** {expr.modifier:+d}")

        except ValueError as e:
            st.error(str(e))

    elif calculate:
        st.warning("Please enter a dice notation.")

    if not calculate:
        st.info("Enter a dice notation above and click **Calculate**.")
        with st.expander("Examples"):
            st.markdown(
                """
                | Notation | Expected |
                |----------|----------|
                | `3d6`    | 10.5 |
                | `2d6+6`  | 13.0 |
                | `5d6`    | 17.5 |
                | `1d20`   | 10.5 |
                | `4d4-2`  | 8.0 |
                """
            )

# =====================================================================
# Page 2: CoC 7e Character Creation Reference
# =====================================================================
elif page == "CoC 7e Reference":
    st.header("CoC 7e Character Creation Reference")

    names = []
    formulas = []
    expected_vals = []
    full_names = []
    for char in COC_CHARACTERISTICS:
        ev = expected_value(parse_notation(char.formula))
        names.append(char.name)
        formulas.append(char.formula)
        expected_vals.append(ev)
        full_names.append(char.full_name)

    total_expected = sum(expected_vals)
    avg_expected = total_expected / len(expected_vals)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Expected (×5)", f"{total_expected:.1f}")
    with col2:
        st.metric("Average per Attribute", f"{avg_expected:.1f}")
    with col3:
        st.metric("Attributes", str(len(expected_vals)))

    st.divider()

    st.subheader("Expected Values by Attribute")
    chart_data = {"Attribute": names, "Expected Value (×5)": expected_vals}
    st.bar_chart(chart_data, x="Attribute", y="Expected Value (×5)", horizontal=True)

    st.subheader("Attribute Details")
    import pandas as pd

    df = pd.DataFrame(
        {
            "Attribute": names,
            "Formula": formulas,
            "Expected (×5)": [f"{v:.1f}" for v in expected_vals],
            "Full Name": full_names,
        }
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("What do these formulas mean?"):
        st.markdown(
            """
            In Call of Cthulhu 7th Edition, characteristics are rolled using
            specific dice formulas:

            - **3d6 × 5** — Used for STR, CON, DEX, POW, APP. Average is 52.5.
            - **2d6+6 × 5** — Used for SIZ, INT, EDU. Average is 65.0.

            The **×5** multiplier converts raw 3-18 scores into the 15-90
            percentile scale used in CoC 7e. The expected values shown are
            theoretical averages over infinite rolls.
            """
        )

# =====================================================================
# Page 3: Roll vs Point-Buy Comparison
# =====================================================================
elif page == "Roll vs Point-Buy":
    st.header("Roll vs Point-Buy Comparison")
    st.markdown(
        "Compare rolling dice (with multiple attempts) against a point-buy budget. "
        "Helps answer: *Is it better to roll X times and pick the best, "
        "or just take X points?*"
    )

    col_input, col_mode = st.columns(2)
    with col_input:
        budget = st.number_input(
            "Point-buy budget",
            min_value=0,
            max_value=1000,
            value=450,
            step=5,
            help="Total points available if you choose point-buy.",
        )
        attempts = st.number_input(
            "Number of attempts (X)",
            min_value=1,
            max_value=50,
            value=3,
            step=1,
            help="Number of complete attribute sets you can roll.",
        )
    with col_mode:
        mode = st.radio(
            "Comparison mode",
            [
                "Best of K Full Sets (Mode A)",
                "Best per Formula Group (Mode B)",
            ],
            help=(
                "Mode A: Pick the best complete set. "
                "Mode B: Pool rolls by formula type."
            ),
        )
        st.markdown(
            "<small>"
            "<b>Mode A:</b> Roll complete sets, pick the best by total sum.<br>"
            "<b>Mode B:</b> Pool all 3d6 rolls together (pick best 5) and all "
            "2d6+6 rolls together (pick best 3). Gives more selection freedom."
            "</small>",
            unsafe_allow_html=True,
        )

    compare = st.button("Compare", use_container_width=True)

    if compare:
        mode_key = "full_set" if "Mode A" in mode else "per_group"
        try:
            with st.spinner("Computing exact probabilities..."):
                result = compare_roll_vs_buy(budget, attempts, mode_key)

            st.divider()

            st.subheader(
                "Mode A — Best of K Full Sets"
                if result.mode == "full_set"
                else "Mode B — Best per Formula Group"
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                delta_val = result.expected_best_total - budget
                st.metric(
                    "Expected Best Total",
                    f"{result.expected_best_total:.1f}",
                    delta=f"{delta_val:+.1f} vs budget",
                    delta_color="normal",
                )
            with col2:
                st.metric("Point-Buy Budget", f"{result.point_buy_total:.1f}")
            with col3:
                st.metric(
                    "Difference",
                    f"{result.difference:+.1f}",
                    delta="Rolling wins!" if result.difference > 0 else "Buying wins!",
                    delta_color="normal",
                )

            if result.difference > 0:
                st.success(result.recommendation)
            elif result.difference < 0:
                st.warning(result.recommendation)
            else:
                st.info(result.recommendation)

            st.divider()

            if result.mode == "full_set":
                single = result.single_set_expected or 0.0
                st.subheader("Mode A — Full Set Breakdown")
                with st.expander("Details", expanded=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Single Set Expected", f"{single:.1f}")
                    with col_b:
                        st.metric(
                            f"Best of {result.attempts} Sets",
                            f"{result.expected_best_total:.1f}",
                            delta=(
                                f"{result.expected_best_total - single:+.1f} "
                                "over single set"
                            ),
                        )
                    st.caption(
                        "Mode A is more constrained: you must take all 8 "
                        "attributes from the same rolled set."
                    )
            else:
                best_3d6 = result.group_3d6_expected_best or 0.0
                best_2d6 = result.group_2d6_expected_best or 0.0
                pool_3d6 = result.group_3d6_pool_size or 0
                pool_2d6 = result.group_2d6_pool_size or 0

                st.subheader("Mode B — Per Group Breakdown")
                with st.expander("Details", expanded=True):
                    st.markdown(
                        f"**Pool:** 5 × 3d6 across {result.attempts} set(s) → "
                        f"**{pool_3d6} rolls**, pick best 5"
                    )
                    st.markdown(
                        f"**Pool:** 3 × 2d6+6 across {result.attempts} set(s) → "
                        f"**{pool_2d6} rolls**, pick best 3"
                    )
                    st.divider()

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Best 3d6 Total", f"{best_3d6:.1f}")
                    with col_b:
                        st.metric("Best 2d6+6 Total", f"{best_2d6:.1f}")
                    with col_c:
                        st.metric("Combined Total", f"{result.expected_best_total:.1f}")

                    st.caption(
                        "Mode B gives more selection freedom: you independently "
                        "optimize within each formula group."
                    )

        except ValueError as e:
            st.error(str(e))
