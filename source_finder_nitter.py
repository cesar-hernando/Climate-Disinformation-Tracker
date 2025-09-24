'''

Tool to find the source of a certain tweet/claim. The pipeline goes as follows:

First, we extract the keywords of the claim using KeyBERT, which we use to build a query 
that can be used for advanced search. 

Secondly, we scrape data from Nitter in order to retrieve tweets with similar content to 
the claim. Nitter is a free and open source alternative Twitter front-end focused on privacy.

Thirdly, we analyze whether the retrieved tweets align or contradict the original claim using 
another LLM, and finally find the oldest aligned tweet.

We use this tool in the context of climate misinformation but it can naturally be used 
in other areas as well.

'''

from scrapper_nitter import ScraperNitter
from query_generator import QueryGenerator
from alignment import AlignmentModel
import time
import pandas as pd
from datetime import datetime
from collections import Counter


class SourceFinder:
    def __init__(self, top_n=5, n=2, excludes={"nativeretweets", "replies"}, batch_size=4):
        self.top_n = top_n
        self.n = n
        self.excludes = excludes
        self.batch_size = batch_size

    @staticmethod
    def _csv_to_dict(filename):
        """
        Converts a csv to a list of dictionaries, renaming some columns for compatibility between classes.
        """

        # Load csv, rename columns and keep only relevant one, and remove empty rows
        df = pd.read_csv(filename)
        df = df.rename(columns={"username": "user", "content": "text", "timestamp":"created_at_datetime"})
        df = df.dropna(subset=["text", "created_at_datetime", "user"], how="all")

        def convert_timestamp_to_iso8601(ts):
            dt = datetime.strptime(ts.replace(" ·", ""), "%b %d, %Y %I:%M %p %Z")
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            
        # Add normalized datetime column
        df["created_at_datetime"] = df["created_at_datetime"].apply(convert_timestamp_to_iso8601)

        # Convert to list of dictionaries
        tweets_list = df.to_dict(orient="records")

        return tweets_list
    
    @staticmethod
    def print_tweet(tweet, separator=80):
        """
        Prints a tweet with all its fields in a nice way to visualize it.
        """
        print("-" * separator)
        for key, value in tweet.items():
            # Capitalize the field name and replace underscores with spaces
            field_name = key.replace("_", " ").capitalize()
            
            # If the value is long text, print on a new line
            if isinstance(value, str) and len(value) > 80:
                print(f"{field_name}:\n{value}")
            else:
                print(f"{field_name}: {value}")
        print("-" * separator)
    

    def run(self, claim, filename, initial_date="", final_date="", verbose=False):
        """
        Transforms a claim into a query for advanced search, retrieves tweets using Nitter, selects the
        tweets that align with the original claim, and obtains the oldest.
        """
        query_generator = QueryGenerator(claim)
        query = query_generator.build_query(top_n=self.top_n, n=self.n)

        scraper = ScraperNitter()
        scraper.get_tweets(query=query, 
                           since=initial_date, 
                           until=final_date, 
                           excludes={"nativeretweets", "replies"}, 
                           filename=filename)
        print(f"\nScraping completed. Tweets saved to {filename}.\n")
        tweets_list = self._csv_to_dict(filename)

        alignment_model = AlignmentModel()
        aligned_tweets = alignment_model.batch_filter_tweets(claim, tweets_list, batch_size=self.batch_size, verbose=verbose)
        if aligned_tweets:
            if verbose:
                print(f"\nAligned tweets:\n{aligned_tweets}")

            oldest_aligned_tweet = alignment_model.find_first(aligned_tweets)
            print(f"\nOldest aligned tweet:\n")
            self.print_tweet(oldest_aligned_tweet)
        else:
            print("No aligned tweets found.")

        return oldest_aligned_tweet, aligned_tweets


    @staticmethod
    def get_top_tweeters(aligned_tweets, N=5):
        """
        Returns the top N usernames with most tweets, number of tweets, and their tweets.
        """
        if not aligned_tweets:
            return []

        # Count tweets per user
        users = [tweet['user'] for tweet in aligned_tweets]
        user_counts = Counter(users)

        # Get top N users
        top_users = user_counts.most_common(N)

        # Collect their tweets
        top_tweeters = []
        for user, count in top_users:
            user_tweets = [tweet['text'] for tweet in aligned_tweets if tweet['user'] == user]
            top_tweeters.append({
                'user': user,
                'tweet_count': count,
                'tweets': user_tweets
            })

        print("\n Top tweeters about this topic...\n")
        for tweeter in top_tweeters:
            print(f"User: {tweeter['user']}  |  Tweets: {tweeter['tweet_count']}")
            for i, tweet in enumerate(tweeter['tweets'], 1):
                print(f"  {i}. {tweet}")
            print("-" * 80)  # separator

        return top_tweeters



if __name__ == "__main__":
    # Define the parameters of the search
    claim = "Electric vehicles are actually worse for environment than gas cars"
    initial_date = ""
    final_date = ""
    n = 1 # No advanced search (# of keywords - n = number of words in each clause)
    filename = f'Electric_cars_worse_n_{n}_{initial_date}_to_{final_date}.csv'
    top_n = 5
    excludes={"nativeretweets", "replies"}
    batch_size = 4
    N = 3 # Top N usernames with more tweets about a topic

    # Execute the source finder tool
    start_time = time.time()
    source_finder = SourceFinder(top_n=top_n, n=n, excludes=excludes, batch_size=batch_size)
    oldest_aligned_tweet, aligned_tweets = source_finder.run(claim, filename, initial_date, final_date)
    top_tweeters = source_finder.get_top_tweeters(aligned_tweets, N)
    end_time = time.time()
    run_time = end_time - start_time
    print(f"\nExecution time of the Source Finder: {run_time} s\n")


