import plotly.express as px
import pandas as pd

def tweets_over_time(df):
    """
    Returns a line chart of posts over time.
    """
    df["created_at_datetime"] = pd.to_datetime(df["created_at_datetime"], errors='coerce')

    labels = {
        0: 'Entailment',
        1: 'Neutral',
        2: 'Contradiction'
    }
    df["alignment"] = df["alignment"].map(labels)
    time_series = df.groupby([df['created_at_datetime'].dt.date, 'alignment']).size().reset_index(name='count')
    # Define fixed colors for each label
    color_map = {
        "Entailment": "green",
        "Neutral": "gray",
        "Contradiction": "red"
    }
    
    fig = px.line(
        time_series,
        x='created_at_datetime',
        y='count',
        color='alignment',
        color_discrete_map=color_map,
        title='Post Frequency Over Time by Alignment',
        render_mode=''
    )

    fig.update_xaxes(title="Time", rangeslider=dict(visible=True), type="date")
    fig.update_yaxes(title="Number of Posts")
    return fig

def top_users(df, top_n=10):
    """
    Returns a bar chart of top users by post count.
    """
    top = df["user"].value_counts().head(top_n).reset_index()
    top.columns = ["user", "count"]
    fig = px.bar(top, x="user", y="count", title=f"Top {top_n} Posters")
    return fig

def tweet_bubble_chart(df):
    """
    Bubble chart of tweets:
    - x-axis: timestamp
    - y-axis: retweet count
    - size: number of comments
    - color: alignment
    """
    # Make sure timestamp is datetime
    df["created_at_datetime"] = pd.to_datetime(df["created_at_datetime"], errors="coerce")
    
    # Map alignment numbers to text (if needed)
    labels = {0: "Entailment", 1: "Neutral", 2: "Contradiction"}
    df["alignment"] = df["alignment"].map(labels)
    
    # Define colors for each alignment
    color_map = {"Entailment": "green", "Neutral": "gray", "Contradiction": "red"}

    # Build the bubble chart
    fig = px.scatter(
        df,
        x="created_at_datetime",
        y="retweets",             # y-axis = number of retweets
        size="likes",          # bubble size = number of comments
        color="alignment",        # bubble color = alignment
        hover_data=["user", "retweets", "comments", "likes"],
        color_discrete_map=color_map,
        title="Posts Bubble Chart",
    )
    
    fig.update_xaxes(title="Time", type="date")
    fig.update_yaxes(title="Number of Retweets", type="log")
    fig.update_traces(marker=dict(sizemode="area", sizeref=2.*max(df["likes"])/(40.**2), line_width=1))
    
    return fig