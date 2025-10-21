from dash import Dash, html, dcc, page_container
from flask import app
import pandas as pd
from visualization.utils.navbar import Navbar

labels = {
        'Entailment': 0,
        'Neutral': 1,
        'Contradiction': 2
    }

def create_app(filename, claim, requests_pathname_prefix="/"):
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
        html.Div([
            html.Span("Show tweets:"),
            dcc.Checklist(
                id="alignment-checklist",
                options=[{"label": label, "value": labels[label]} for label in labels.keys()],
                value=list(labels.values()),  # default: all
                style={"marginTop": "4px"}
            )
        ], className="alignment-filter"),
        html.Div(page_container, style={"padding": "10px"})
    ])

    return app


if __name__ == "__main__":
    # Example usage
    # run python -m visualization.app to test the visualization
    filename ="./data/electric_gas_worse_environment_cars_kpc_4_2006-03-21_to_2025-10-21_no_replies.csv"
    claim = "Electric cars are worse for the environment than gas cars"
    app = create_app(filename, claim)
    app.run(debug=True)
