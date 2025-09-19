from keybert import KeyBERT
from itertools import combinations
import tweepy

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAMAv4AEAAAAA%2FPo%2BLnj5RdYZytVUwY59lx4QDv0%3Dfi3nRbMoTjOepGlXo24cbFaVwg42ETbdJdODjFilp1qEnpMe4F"
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

def extract_keywords(text):
    """Extract keywords from text using KeyBERT"""
    kw_model = KeyBERT(model="AIDA-UPM/mstsb-paraphrase-multilingual-mpnet-base-v2")
    keywords = kw_model.extract_keywords(text, top_n=5)
    print(keywords)
    keywords = [k[0] for k in keywords]
    return keywords


def build_query(keywords, n=1):
    """Generate OR-combinations of keywords with AND inside each group"""
    queries = []
    for i in range(len(keywords) - n, len(keywords)):
        for combo in combinations(keywords, i):
            queries.append("(" + " AND ".join(combo) + ")")
    return " OR ".join(queries)


def search_tweets(query, max_results=10):
    """Search tweets using the Twitter API"""
    tweets = client.search_all_tweets(query=query, max_results=max_results)
    return tweets


text = "Current studies that conclude climate change is accelerating are invalid because they do not account for natural climate variability."
# keywords = extract_keywords(text)
# query = build_query(keywords, n=2)
query = "(climate AND change)"
tweets = search_tweets(query, max_results=1)
print(tweets)