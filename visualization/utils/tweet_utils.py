import ast
from dash import html

def TweetCard(tweet):
    tweet_url = f"https://twitter.com{tweet['link']}"  # Construct the tweet URL
    user_url = f"https://twitter.com/{tweet['user']}"  # Construct the user's profile URL

    # Build "Replying to" / "Quoting" text
    reply_to = tweet.get("replying-to")
    quoting = tweet.get("quoting")

    reply_html = None
    if reply_to and isinstance(reply_to, str):
        try:
            reply_list = ast.literal_eval(reply_to)
        except:
            reply_list = [reply_to]
        if len(reply_list) > 0:
            reply_html = html.Div(
                ["Replying to:"] + [
                    html.A(f"{u}", href=f"https://twitter.com/{u}", target="_blank", className="reply-tag")
                    for u in reply_list
                ],
                className="replying-to"
            )

    quoting_html = None
    if quoting and isinstance(quoting, str) and quoting.strip():
        quoting_html = html.Div(
            [
                "Quoting: ",
                html.A(f"{quoting}", href=f"https://twitter.com/{quoting}", target="_blank", className="quote-tag")
            ],
            className="quoting"
        )


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
            reply_html if reply_html else None,
            quoting_html if quoting_html else None,
            html.Div(tweet["text"], className="tweet-content"),
            html.Div([
                html.Span(f"💬 {tweet.get('comments', 0)}", className="tweet-stats-middle"),
                html.Span(f"🔁 {tweet.get('retweets', 0)}", className="tweet-stats-middle"),
                html.Span(f"❤️ {tweet.get('likes', 0)}", className="tweet-stats-middle"),
                html.Span(f"💭 {tweet.get('quotes', 0)}"),
            ], className="tweet-stats")
        ], className="tweet-card")
    )

def TweetList(tweets):
    return html.Div(
        [TweetCard(tweet) for tweet in tweets],
        className="tweet-list"
    )
