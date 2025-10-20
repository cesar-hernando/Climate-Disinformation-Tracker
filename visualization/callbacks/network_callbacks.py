from dash import callback, Input, Output, html
import pandas as pd
from visualization.utils.graph_utils import build_graph, nx_to_cyto
from visualization.utils.tweet_utils import TweetList

def register_callbacks():
    @callback(
        Output("tweet-network", "elements"),
        Input("data-store", "data"),
        Input("interaction-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date")
    )
    def update_network(data, selected, start_date, end_date):
        data = pd.DataFrame(data)
        data["created_at_datetime"] = pd.to_datetime(data["created_at_datetime"], errors='coerce')
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

        info = f"User: {user} | Tweets: {len(user_tweets)}"
        if user_tweets.empty:
            return info, html.Div("No tweets in this period.", style={"color": "gray", "textAlign": "center"})

        tweets = user_tweets.to_dict("records")
        return info, TweetList(tweets)