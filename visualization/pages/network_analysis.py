import pandas as pd
from dash import html, dcc, register_page
import dash_cytoscape as cyto
from visualization.callbacks import network_callbacks

register_page(__name__, path='/network', name='Network Analysis')

def layout(**kwargs):
    return html.Div([
        html.Div([
            html.Label("Date Range:"),
            dcc.DatePickerRange(
                id="date-range",
                display_format="YYYY-MM-DD"
            ),
            dcc.Checklist(
                    id="interaction-filter",
                    options=[
                        {"label": html.Span([
                            "Replies ",
                            html.Span(style={"borderBottom": "2px solid #555", "width": "20px", "display": "inline-block", "marginLeft": "5px", "verticalAlign": "middle"})
                        ]), "value": "reply"},
                        {"label": html.Span([
                            "Quotes ",
                            html.Span(style={"borderBottom": "2px dashed #555", "width": "20px", "display": "inline-block", "marginLeft": "5px", "verticalAlign": "middle"})
                        ]), "value": "quote"}
                    ],
                    value=["reply", "quote"],
                    inline=True,
                    labelStyle={"display": "inline-flex", "alignItems": "center", "marginRight": "10px"}
                ),
            html.Div(id="no-replies-message")

        ], style={"textAlign": "center", "marginBottom": "10px", "display": "flex", "justifyContent": "center", "gap": "20px", "alignItems": "center"}),

        html.Div(id="network-graph-container", children=[
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
                            # Replies will be a solid line
                            "selector": '[interaction = "reply"]',
                            "style": {
                                "line-style": "solid"
                            }
                        },
                        {
                            # Quotes will be a dashed line
                            "selector": '[interaction = "quote"]',
                            "style": {
                                "line-style": "dashed"
                            }
                        },
                        {
                            "selector": '[alignment = 0]', 
                            "style": {
                                "line-color": "#07C255",
                                "target-arrow-color": "#07C255"
                            }
                        },
                        {
                            "selector": '[alignment = 1]', 
                            "style": {
                                "line-color": "#8D8D8D", 
                                "target-arrow-color": "#8D8D8D"
                            }
                        },
                        {
                            "selector": '[alignment = 2]', 
                            "style": {
                                "line-color": "#C52A2A",
                                "target-arrow-color": "#C52A2A"
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
        ], style={"display": "block"}),

        html.Div(id="no-graph-message", style={"textAlign": "center"})
    ])

network_callbacks.register_callbacks()