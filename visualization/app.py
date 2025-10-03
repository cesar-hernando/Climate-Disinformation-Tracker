from dash import Dash
import pandas as pd
from . import layout, callbacks

def run_app(df: pd.DataFrame, claim: str, debug: bool = False, use_reloader: bool = False):
    app = Dash(__name__, title="Dashboard")

    # Assign layout
    app.layout = layout.create_layout(df, claim)

    # Register callbacks
    callbacks.register_callbacks(app)

    app.run(debug=debug, use_reloader=use_reloader)


if __name__ == "__main__":
    # Example usage
    # run python -m visualization.app to test the visualization
    df = pd.read_csv("./data/climate_caused_sun_natural_cycles_kpc_4_2006-03-21_to_2025-10-03.csv")
    df["text"] = (
                df["text"]
                .str.replace(r"\\n", "\n", regex=True)   # turn \n into newline
                .str.strip('"\'')                        # remove wrapping quotes
            )
    claim = "Climate change is just caused by natural cycles of the sun"
    run_app(df, claim, debug=True, use_reloader=True)