from dash import html

def TweetCard(tweet):
    tweet_url = f"https://twitter.com{tweet['link']}"  # Construct the tweet URL
    user_url = f"https://twitter.com/{tweet['user']}"  # Construct the user's profile URL

    return html.A(
        href=tweet_url,  # Link to the original tweet
        target="_blank",  # Open in a new tab
        children=html.Div([
            html.Div([
                html.A(
                    tweet["user"],  # Username as clickable text
                    href=user_url,  # Link to the user's profile
                    target="_blank",  # Open in a new tab
                    className="tweet-username"
                ),
                html.Span(tweet["created_at_datetime"].strftime("%b %d, %Y %H:%M"), className="tweet-timestamp"),
            ], className="tweet-header"),
            html.Div(tweet["text"], className="tweet-content"),
            html.Div([
                html.Span(f"💬 {tweet.get('comments', 0)}", className="tweet-comments"),
                html.Span(f"🔁 {tweet.get('retweets', 0)}", className="tweet-retweets"),
                html.Span(f"❤️ {tweet.get('likes', 0)}", className="tweet-likes"),
            ], className="tweet-stats")
        ], className="tweet-card")
    )

def TweetList(tweets):
    return html.Div(
        [TweetCard(tweet) for tweet in tweets],
        className="tweet-list"
    )
