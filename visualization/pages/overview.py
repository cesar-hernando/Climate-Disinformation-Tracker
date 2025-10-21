from dash import dcc, html, register_page
import pandas as pd
from visualization.callbacks import callbacks

register_page(__name__, path='/', name='Overview')

def layout(**kwargs):
    return html.Div([
        html.Div(
            [
                html.H4(
                    "First Found Entailing Tweet",
                    style={ "textAlign": "left", "marginBottom": "8px", "marginLeft": "8px", "fontWeight": "600" },
                ),
                html.Div(id="first-entailment-tweet"),
            ],
            style={"marginTop": "25px", "marginBottom": "15px"},
        ),

        # Bubble chart row: Bubble Chart + Selected Tweet
        html.Div([
            html.Div([
                dcc.Graph(id="bubble-chart")
            ], id="bubble-chart-container", style={"flex": "3", "marginRight": "0px"}),

            html.Div(
                id="selected-tweet",
                style={
                    "flex": "1",
                    "padding": "10px"
                }
            )
        ], style={"display": "flex", "flexDirection": "row", "marginTop": "20px", "height": "600px"}),

        dcc.Store(id="selection-store", data={"date": None, "user": None}),

        # Top row: Left side (Time Series above Top Users), Right side (Tweet List)
        html.Div([
            # Left side
            html.Div([
                dcc.Graph(id="time-series", style={"flex": "0.6"}),
                dcc.Graph(id="top-users", style={"flex": "0.4"})
            ], style={"flex": "2", "display": "flex", "flexDirection": "row", "marginRight": "10px"}),

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
                ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "margin": "10px 0"}),

                
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
        ], style={"display": "flex", "flexDirection": "column", "margin": "10px 0"}),

    ])

callbacks.register_callbacks()