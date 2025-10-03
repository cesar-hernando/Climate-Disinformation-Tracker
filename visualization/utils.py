from dash import html

def TweetCard(tweet):
    return html.Div([
        html.Div([
            html.Span(tweet["user"], className="tweet-username"),
            html.Span(tweet["created_at_datetime"].strftime("%b %d, %Y %H:%M"), className="tweet-timestamp"),
        ], className="tweet-header"),
        html.Div(tweet["text"], className="tweet-content"),
        html.Div([
            html.Span(f"💬 {tweet.get('comments', 0)}", className="tweet-comments"),
            html.Span(f"🔁 {tweet.get('retweets', 0)}", className="tweet-retweets"),
            html.Span(f"❤️ {tweet.get('likes', 0)}", className="tweet-likes"),
        ], className="tweet-stats")
    ], className="tweet-card")

def TweetList(tweets):
    return html.Div(
        [TweetCard(tweet) for tweet in tweets],
        className="tweet-list"
    )
