from dash import Dash, Input, Output, dcc, html
import pandas as pd
from . import layout, callbacks
from urllib.parse import parse_qs, urlparse

def run_app(filename: str, claim: str, debug: bool = False, use_reloader: bool = False):
    """
    Runs the Dash web application for visualizing climate disinformation data.
    Args:
        filename (str): The path to the CSV file containing the data to be visualized.
        claim (str): The claim to be highlighted in the dashboard.
        debug (bool, optional): If True, runs the app in debug mode. Defaults to False.
        use_reloader (bool, optional): If True, enables the Dash reloader. Defaults to False.
    Returns:
        None
    """
    df = pd.read_csv(filename)

    df["text"] = df["text"].str.replace(r"\\n", "\n", regex=True).str.strip('"\'')  # turn \n into newline and remove wrapping quotes

    app = Dash(__name__, title="Visualization")

    # Assign layout
    app.layout = layout.create_layout(df, claim)

    # Register callbacks
    callbacks.register_callbacks(app)

    app.run(debug=debug, use_reloader=use_reloader)

def create_app(filename, claim):
    """
    Creates and configures a Dash web application that can be mounted using FastAPI.
    Args:
        filename (str): Path to the CSV file containing the data to visualize.
        claim (str): The claim to be highlighted in the dashboard.
    Returns:
        dash.Dash: A configured Dash application instance with layout and callbacks registered.
    """
    df = pd.read_csv(filename)
    df["text"] = df["text"].str.replace(r"\\n", "\n", regex=True).str.strip('"\'')  # turn \n into newline and remove wrapping quotes
    
    path = filename.split("data/", maxsplit=1)[-1].replace(".csv", "")
    app = Dash(__name__, title="Visualization", requests_pathname_prefix=f"/visualization/{path}/")

    # Assign layout
    app.layout = layout.create_layout(df, claim)

    # Register callbacks
    callbacks.register_callbacks(app)

    return app


if __name__ == "__main__":
    # Example usage
    # run python -m visualization.app to test the visualization
    filename ="./data/climate_caused_sun_natural_cycles_kpc_4_2006-03-21_to_2025-10-06.csv"
    claim = "Climate change is just caused by natural cycles of the sun"
    run_app(filename, claim, debug=True, use_reloader=True)