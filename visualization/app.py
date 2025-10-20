from dash import Dash, html, dcc, page_container
from flask import app
import pandas as pd
from visualization.utils.navbar import Navbar

def create_app(filename, claim, requests_pathname_prefix=None):
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
    
    app = Dash(__name__, title="Visualization", use_pages=True, requests_pathname_prefix=requests_pathname_prefix)

    app.layout = html.Div([
        dcc.Store(id='data-store', data=df.to_dict('records')),
        Navbar(claim_text=claim, path=requests_pathname_prefix),
        html.Div(page_container, style={"padding": "10px"})
    ])

    return app


if __name__ == "__main__":
    # Example usage
    # run python -m visualization.app to test the visualization
    filename ="./data/climate_caused_sun_natural_cycles_kpc_4_2006-03-21_to_2025-10-16_.csv"
    claim = "Climate change is just caused by natural cycles of the sun"
    app = create_app(filename, claim)
    app.run(debug=True)
