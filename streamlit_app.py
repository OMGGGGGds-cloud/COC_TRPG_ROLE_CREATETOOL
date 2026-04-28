"""Entry point for `streamlit run streamlit_app.py` from the project root.

The full Streamlit app lives in dice_calc/streamlit_ui.py.
"""

from dice_calc.streamlit_ui import run_web

if __name__ == "__main__":
    run_web()
