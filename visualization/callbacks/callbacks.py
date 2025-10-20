from dash import Input, Output, ctx, html, dcc, callback
import pandas as pd

from visualization.utils import figures
from visualization.utils.tweet_utils import TweetList, TweetCard

def register_callbacks():

    @callback(
        Output("first-entailment-tweet", "children"),
        Input("data-store", "data")
    )
    def update_first_entailment(data):
        df = pd.DataFrame(data)
        df["created_at_datetime"] = pd.to_datetime(df["created_at_datetime"], errors='coerce')
        # Filter for ENTAILMENT tweets
        entailment_tweets = df[df['alignment'] == 0]
        if entailment_tweets.empty:
            return "No entailment tweets found."
        # Find earliest tweet
        first_tweet = entailment_tweets.sort_values("created_at_datetime").iloc[0]
        return TweetCard(first_tweet)
    
    @callback(
        Output("time-series", "figure"),
        Input("data-store", "data"),
        Input("alignment-checklist", "value") 
    )
    def update_time_series(data, selected_alignments):
        df = pd.DataFrame(data)
        df["created_at_datetime"] = pd.to_datetime(df["created_at_datetime"], errors='coerce')
        if selected_alignments:
            df = df[df['alignment'].isin(selected_alignments)]
        return figures.tweets_over_time(df)

    @callback(
        Output("top-users", "figure"),
        Input("data-store", "data"),
        Input("alignment-checklist", "value")
    )
    def update_top_users(data, selected_alignments):
        df = pd.DataFrame(data)
        if selected_alignments:
            df = df[df['alignment'].isin(selected_alignments)]
        return figures.top_users(df)
    
    @callback(
        Output("bubble-chart", "figure"),
        Input("data-store", "data"),
        Input("alignment-checklist", "value") 
    )
    def update_bubble_chart(data, selected_alignments):
        df = pd.DataFrame(data)
        if selected_alignments:
            df = df[df['alignment'].isin(selected_alignments)]
        return figures.tweet_bubble_chart(df)
    
    @callback(
        Output("selection-store", "data"),
        Input("time-series", "clickData"),
        Input("top-users", "clickData"),
        Input("reset-date", "n_clicks"),
        Input("reset-user", "n_clicks"),
        Input("selection-store", "data")
    )
    def update_selection(time_click, user_click, reset_date, reset_user, current):
        triggered = ctx.triggered_id
        if current is None:
            current = {"date": None, "user": None}

        if triggered == "time-series" and time_click:
            clicked_date = pd.to_datetime(time_click["points"][0]["x"]).date()
            current["date"] = clicked_date

        elif triggered == "top-users" and user_click:
            current["user"] = user_click["points"][0]["x"]

        elif triggered == "reset-date":
            current["date"] = None

        elif triggered == "reset-user":
            current["user"] = None

        return current
    
    @callback(
        Output("selection-info", "children"),
        Input("selection-store", "data")
    )
    def update_selection_info(selection):
        if not selection.get("date") and not selection.get("user"):
            return "No filters applied."

        parts = []
        if selection.get("date"):
            parts.append(f"📅 {selection['date']}")
        if selection.get("user"):
            parts.append(f"👤 {selection['user']}")

        return " | ".join(parts)


    @callback(
        Output("tweet-list", "children"),
        Input("selection-store", "data"),
        Input("data-store", "data"),
        Input("alignment-checklist", "value")
    )
    def display_tweets(selection, data, selected_alignments):
        df = pd.DataFrame(data)
        df["created_at_datetime"] = pd.to_datetime(df["created_at_datetime"], errors='coerce')

        # Filter by alignment
        if selected_alignments:
            df = df[df['alignment'].isin(selected_alignments)]

        if not selection.get("date") and not selection.get("user"):
            return "Click on a date or user to filter posts."

        # Apply filters
        if selection.get("date"):
            selection["date"] = pd.to_datetime(selection["date"], errors='coerce').date()
            df = df[df["created_at_datetime"].dt.date == selection["date"]]

        if selection.get("user"):
            df = df[df["user"] == selection["user"]]

        if df.empty:
            return "No tweets found."

        return TweetList(df.to_dict('records'))
    
    @callback(
        Output("selected-tweet", "children"),
        Input("bubble-chart", "clickData"),
        Input("data-store", "data")
    )
    def show_selected_bubble(clickData, data):
        df = pd.DataFrame(data)
        df["created_at_datetime"] = pd.to_datetime(df["created_at_datetime"], errors="coerce")

        if not clickData:
            return "Click a bubble to see the post here."

        # Get clicked bubble
        point = clickData["points"][0]
        timestamp = pd.to_datetime(point["x"]).date()
        username = point["customdata"][0]  # adjust based on hover_data

        # Find the clicked tweet
        tweet = df[(df["created_at_datetime"].dt.date == timestamp) & (df["user"] == username)]
        if tweet.empty:
            return "Post not found."

        tweet = tweet.iloc[0]

        return TweetCard(tweet)






