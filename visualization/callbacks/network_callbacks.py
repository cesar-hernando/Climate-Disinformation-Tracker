from dash import callback, Input, Output, html
import pandas as pd
from visualization.utils.graph_utils import build_graph, nx_to_cyto
from visualization.utils.tweet_utils import TweetList

def register_callbacks():
    @callback(
        Output("network-graph-container", "style"),
        Output("no-graph-message", "children"),
        Input("tweet-network", "elements"),
    )
    def toggle_graph_visibility(elements):
        """
        This callback shows the graph container only if there are edges
        (i.e., replies or quotes) in the network data.
        """
        if elements:
            # Check if any element in the list is an edge
            has_edges = any(el.get("data") for el in elements)
            if has_edges:
                # If edges exist, show the container
                return {'display': 'block'}, ""
        
        # If no elements or no edges, keep container hidden
        return {'display': 'none'}, "No interactions to display. Please ensure that your data contains replies or quotes."

    @callback(
        Output("no-replies-message", "children"),
        Output("interaction-filter", "options"),
        Input("tweet-network", "elements"),
    )
    def display_no_replies_message(elements):
        if not any(el.get("data").get("interaction") == "reply" for el in elements):
            return html.Div(
                "* Please include replies in data to visualize reply interactions.",
                style={"color": "red", "fontSize": "12px"}
            ), [
                        {"label": html.Span([
                            "Quotes ",
                            html.Span(style={"borderBottom": "2px dashed #555", "width": "20px", "display": "inline-block", "marginLeft": "5px", "verticalAlign": "middle"})
                        ]), "value": "quote"}
                    ]
        return "", [
                        {"label": html.Span([
                            "Replies ",
                            html.Span(style={"borderBottom": "2px solid #555", "width": "20px", "display": "inline-block", "marginLeft": "5px", "verticalAlign": "middle"})
                        ]), "value": "reply"},
                        {"label": html.Span([
                            "Quotes ",
                            html.Span(style={"borderBottom": "2px dashed #555", "width": "20px", "display": "inline-block", "marginLeft": "5px", "verticalAlign": "middle"})
                        ]), "value": "quote"}
                    ]

    
    @callback(
        Output("tweet-network", "elements"),
        Input("data-store", "data"),
        Input("interaction-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("alignment-checklist", "value") 
    )
    def update_network(data, selected, start_date, end_date, selected_alignments):
        data = pd.DataFrame(data)
        data["created_at_datetime"] = pd.to_datetime(data["created_at_datetime"], errors='coerce')
        if selected_alignments:
            data = data[data['alignment'].isin(selected_alignments)]
        include_replies = "reply" in selected
        include_quotes = "quote" in selected

        mask = (data["created_at_datetime"].dt.date >= pd.to_datetime(start_date).date()) & \
            (data["created_at_datetime"].dt.date <= pd.to_datetime(end_date).date())
        df_filtered = data.loc[mask]

        G = build_graph(df_filtered, include_replies, include_quotes)
        return nx_to_cyto(G)

    @callback(
        Output("node-info", "children"),
        Output("user-tweets", "children"),
        Input("data-store", "data"),
        Input("tweet-network", "tapNodeData"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date")
    )
    def display_user_tweets(data, node_data, start_date, end_date):
        if not node_data:
            return "Click a node to see user details.", html.Div("")
        
        data = pd.DataFrame(data)
        data["created_at_datetime"] = pd.to_datetime(data["created_at_datetime"], errors='coerce')

        user = node_data["label"]
        mask = (data["created_at_datetime"].dt.date >= pd.to_datetime(start_date).date()) & \
            (data["created_at_datetime"].dt.date <= pd.to_datetime(end_date).date())
        user_tweets = data.loc[mask & (data["user"] == user)].sort_values("created_at_datetime", ascending=False)
        user_link = f"https://twitter.com/{user}"

        user_info = html.Div([
            html.Span("User: "),
            html.A(f"{user}", href=user_link, target="_blank", className="tweet-username"),
            html.Span(f" | Tweets: {len(user_tweets)}", style={"marginLeft": "10px", "fontWeight": "normal", "color": "#555"})
        ], style={"textAlign": "center", "marginBottom": "10px"})



        if user_tweets.empty:
            return user_info, html.Div("No tweets in this period.", style={"color": "gray", "textAlign": "center"})

        tweets = user_tweets.to_dict("records")
        return user_info, TweetList(tweets)
    
    @callback(
        Output("date-range", "min_date_allowed"),
        Output("date-range", "max_date_allowed"),
        Output("date-range", "start_date"),
        Output("date-range", "end_date"),
        Input("data-store", "data")
    )
    def update_datepicker_range(data):
        # Convert data back to DataFrame if stored as dict
        df = pd.DataFrame(data)

        # Drop missing dates
        df["created_at_datetime"] = pd.to_datetime(df["created_at_datetime"], errors="coerce")
        df = df.dropna(subset=["created_at_datetime"])

        min_date = df["created_at_datetime"].min().date()
        max_date = df["created_at_datetime"].max().date()

        return min_date, max_date, min_date, max_date