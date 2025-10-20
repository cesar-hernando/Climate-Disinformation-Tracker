import pandas as pd
from dash import html, dcc, register_page
import dash_cytoscape as cyto
from visualization.callbacks import network_callbacks

filename = "test_Earth_warmed_cooled_2023-01-01_to_2025-10-01.csv"

df = pd.read_csv(filename)
df["text"] = df["text"].str.replace(r"\\n", "\n", regex=True).str.strip('"\'')  # turn \n into newline and remove wrapping quotes
df["created_at_datetime"] = pd.to_datetime(df["created_at_datetime"], errors="coerce")
df = df.dropna(subset=["created_at_datetime"])

# --------------------------------------------------
# 4. Dash App
# --------------------------------------------------
register_page(__name__, path='/network', name='Network Analysis')

def layout(**kwargs):
    return html.Div([

        html.Div([
            html.Label("Date Range:"),
            dcc.DatePickerRange(
                id="date-range",
                min_date_allowed=df["created_at_datetime"].min().date(),
                max_date_allowed=df["created_at_datetime"].max().date(),
                start_date=df["created_at_datetime"].min().date(),
                end_date=df["created_at_datetime"].max().date(),
                display_format="YYYY-MM-DD"
            ),
            dcc.Checklist(
                id="interaction-filter",
                options=[
                    {"label": "Replies", "value": "reply"},
                    {"label": "Quotes", "value": "quote"}
                ],
                value=["reply", "quote"],
                inline=True
            )
        ], style={"textAlign": "center", "marginBottom": "10px", "display": "flex", "justifyContent": "center", "gap": "20px", "alignItems": "center"}),

        html.Div([
            html.Div([
                cyto.Cytoscape(
                    id="tweet-network",
                    layout={"name": "cose"},
                    style={"width": "100%", "height": "600px"},
                    elements=[],
                    stylesheet=[
                        {
                            "selector": "node",
                            "style": {
                                "content": "data(label)",
                                "background-color": "#0074D9",
                                "width": "mapData(centrality, 0, 0.1, 10, 60)",
                                "height": "mapData(centrality, 0, 0.1, 10, 60)",
                                "font-size": "8px"
                            }
                        },
                        {
                            "selector": "edge",
                            "style": {
                                "curve-style": "bezier",
                                "target-arrow-shape": "triangle",
                                "arrow-scale": 1,
                                "width": 1.2,
                                "opacity": 0.8
                            }
                        },
                        {
                            "selector": '[interaction = "reply"]',
                            "style": {
                                "line-color": "#00CC96",
                                "target-arrow-color": "#00CC96"
                            }
                        },
                        {
                            "selector": '[interaction = "quote"]',
                            "style": {
                                "line-color": "#FF851B",
                                "target-arrow-color": "#FF851B"
                            }
                        }
                    ],
                )
            ], style={"width": "65%", "display": "inline-block", "verticalAlign": "top"}),

            html.Div([
                html.Div(id="node-info", style={"textAlign": "center", "marginBottom": "10px"}),
                html.Div(id="user-tweets", className="tweet-container", style={
                    "maxHeight": "600px",
                    "overflowY": "auto",
                    "padding": "0 10px"
                })
            ], style={
                "width": "33%",
                "display": "inline-block",
                "verticalAlign": "top",
                "paddingLeft": "10px"
            })
        ])
    ])

network_callbacks.register_callbacks()