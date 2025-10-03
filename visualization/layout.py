from dash import dcc, html
import pandas as pd

def create_layout(df: pd.DataFrame, claim: str):
    labels = {
        'Entailment': 0,
        'Neutral': 1,
        'Contradiction': 2
    }

    return html.Div([
        html.H1("Source Finder", style={"text-align": "center"}),

        # Store the dynamic data
        dcc.Store(id='data-store', data=df.to_dict('records')),

        html.H2(f"Claim: {claim}", style={"text-align": "center", "font-size": "20px", "font-weight": "normal", "margin-top": "0"}),

        html.Div(id="first-entailment-tweet"),

        html.Div([
            html.Span("Show tweets:"),
            dcc.Checklist(
                id="alignment-checklist",
                options=[{"label": label, "value": labels[label]} for label in labels.keys()],
                value=list(labels.values()),  # default: all
                style={"margin-top": "4px"}
            )
        ], className="alignment-filter"),

        # Bubble chart row: Bubble Chart + Selected Tweet
        html.Div([
            html.Div([
                dcc.Graph(id="bubble-chart")
            ], id="bubble-chart-container", style={"flex": "3", "margin-right": "0px"}),

            html.Div(
                id="selected-tweet",
                style={
                    "flex": "1",
                    "padding": "10px"
                }
            )
        ], style={"display": "flex", "flex-direction": "row", "margin-top": "20px", "height": "600px"}),

        dcc.Store(id="selection-store", data={"date": None, "user": None}),

        # Top row: Left side (Time Series above Top Users), Right side (Tweet List)
        html.Div([
            # Left side
            html.Div([
                dcc.Graph(id="time-series", style={"flex": "0.6"}),
                dcc.Graph(id="top-users", style={"flex": "0.4"})
            ], style={"flex": "2", "display": "flex", "flex-direction": "row", "margin-right": "10px"}),

            # Right side (tweet list + title + buttons)
            html.Div([
                html.Div([
                # Info box
                html.Div(id="selection-info", className="selection-info"),

                # Reset buttons
                html.Div([
                        html.Button("Remove Date Filter", id="reset-date", n_clicks=0, className="reset-button"),
                        html.Button("Remove User Filter", id="reset-user", n_clicks=0, className="reset-button")
                    ], className="reset-buttons")
                ], style={"display": "flex", "justify-content": "space-between", "align-items": "center", "margin": "10px 0"}),

                
                # Scrollable tweet list
                html.Div(
                    id="tweet-list",
                    style={
                        "overflow-y": "scroll",
                        "max-height": "500px",
                        "border": "1px solid #ccc",
                        "padding": "10px",
                        "border-radius": "8px",
                        "background-color": "#f9f9f9",
                        "margin-bottom": "10px"
                    }
                ),
            ], style={"flex": "1"})
        ], style={"display": "flex", "flex-direction": "column", "margin": "10px 0"}),

    ])
