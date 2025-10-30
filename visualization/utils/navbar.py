from dash import html, dcc

def Navbar(claim_text, path=None):
    """Modern transparent navbar with centered title and animated buttons."""
    return html.Nav(
        className="navbar",
        children=[
            # Left: Button group
            html.Div([
                dcc.Link("Overview", href=path, className="nav-btn btn-left"),
                dcc.Link("Network Analysis", href=path + "network", className="nav-btn btn-right"),
            ], className="btn-group"),

            # Center: Title + Claim stacked vertically
            html.Div([
                html.Div("Climate Disinformation Tracker", className="navbar-title"),
                html.Div(claim_text, className="navbar-claim"),
            ], className="navbar-center"),

            # Right spacer for layout symmetry
            html.Div(className="navbar-spacer"),
        ]
    )
