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
from datetime import date
from collections import Counter


class SourceFinder:
    def __init__(self, top_n=5, n=2, excludes={"nativeretweets", "replies"}, batch_size=4):
        self.top_n = top_n # Number of keywords extracted by KeyBert
        self.n = n # Number of keywords dropped per clause
        self.excludes = excludes
        self.batch_size = batch_size
    

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
    

    def find_all(self, claim, initial_date="", final_date="", verbose=False):
        """
        Transforms a claim into a query for advanced search, retrieves tweets using Nitter, selects the
        tweets that align with the original claim, and obtains the oldest.
        """
        query_generator = QueryGenerator(claim)
        keywords = query_generator.extract_keywords(top_n=self.top_n)
        query = query_generator.build_query(n=self.n, keywords=keywords)
        if initial_date == "":
            initial_date = "2006-03-21" # Beginning of Twitter

        if final_date == "":
            final_date = date.today().strftime("%Y-%m-%d")

        filename = "_".join(keywords) + f'_kpc_{self.top_n - self.n}_{initial_date}_to_{final_date}.csv' # kpc stands for keywords per clause

        scraper = ScraperNitter()
        tweets_list = scraper.get_tweets(query=query, 
                           since=initial_date, 
                           until=final_date, 
                           excludes={"nativeretweets", "replies"}, 
                           filename=filename)
        scraper.close()
        if tweets_list:
            print(f"\nScraping completed satisfactorily. Tweets saved to {filename}.\n")
        else:
            print(f"\nError encountered and no tweets were retrieved.\n")
            return None, None

        alignment_model = AlignmentModel()
        aligned_tweets = alignment_model.batch_filter_tweets(claim, tweets_list, batch_size=self.batch_size, verbose=verbose)
        if aligned_tweets:
            if verbose:
                print(f"\nAligned tweets:\n{aligned_tweets}")

            oldest_aligned_tweet = alignment_model.find_first(aligned_tweets)
            print(f"\nOldest aligned tweet:\n")
            self.print_tweet(oldest_aligned_tweet)

            return oldest_aligned_tweet, aligned_tweets
        else:
            print("No aligned tweets found.")
            return None, None
        

    def find_source(self, claim, initial_date="", final_date="", step=1):
        """
        The workflow is similar to the method find_all but here we search in steps
        of step years, starting from the initial_date, and we stop once an aligned 
        tweet is found.
        """
        query_generator = QueryGenerator(claim)
        keywords = query_generator.extract_keywords(top_n=self.top_n)
        query = query_generator.build_query(n=self.n, keywords=keywords)

        if initial_date == "":
            initial_date = "2006-03-21" # Beginning of Twitter

        if final_date == "":
            final_date = date.today().strftime("%Y-%m-%d")

        # Extract year from date
        initial_year = int(initial_date[:4])
        final_year = int(final_date[:4])

        prov_initial_year = initial_year
        prov_final_year = initial_year + step

        scraper = ScraperNitter()
        alignment_model = AlignmentModel()

        while prov_final_year <= (final_year + 1):
            # Construct dates from the corresponding years and the original initial month and day
            prov_initial_date = str(prov_initial_year) + initial_date[4:]
            prov_final_date = str(prov_final_year) + initial_date[4:]

            print(f"\nRetrieving tweets from {prov_initial_date} to {prov_final_date}...")
            filename = "_".join(keywords) + f'_kpc_{self.top_n - self.n}_{prov_initial_date}_to_{prov_final_date}.csv' # kpc stands for keywords per clause

            tweets_list = scraper.get_tweets(query=query, 
                           since=prov_initial_date, 
                           until=prov_final_date, 
                           excludes={"nativeretweets", "replies"},
                           save_csv=False, 
                           filename=filename)
            
            if tweets_list:
                print(f"Scraping completed satisfactorily.")
            else:
                print(f"Error encountered and no tweets were retrieved.")
                prov_initial_year += step
                prov_final_year += step
                continue

            aligned_tweets = alignment_model.batch_filter_tweets(claim, tweets_list, batch_size=self.batch_size)

            if aligned_tweets:
                oldest_aligned_tweet = alignment_model.find_first(aligned_tweets)
                print("\nOldest aligned tweet:")
                self.print_tweet(oldest_aligned_tweet)
                return oldest_aligned_tweet, aligned_tweets
            else:
                print("None of the tweets are aligned.")
                prov_initial_year += step
                prov_final_year += step
                continue

        scraper.close()
        print("\nNo aligned tweets were found between the dates provided\n")
        return None, None    
            

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
    claim = "The earth was hotter in the past, the medieval warm piored. Why is Greenland called Greenland?.the last ice age Co2 was high."
    top_n = 5 # Number of keywords extracted
    n = 1 # No advanced search if n=0 (# of keywords - n = number of words in each clause)
    excludes={"nativeretweets", "replies"}
    batch_size = 4 
    N = 3 # Top N usernames with more tweets about a topic

    mode = 0 # 0 (find source) or 1 (retrieve all)

    start_time = time.time()
    source_finder = SourceFinder(top_n=top_n, n=n, excludes=excludes, batch_size=batch_size)

    if mode == 0:
        initial_date = "2007-01-01"
        final_date = "2020-01-01"
        step = 1
        oldest_aligned_tweet, aligned_tweets = source_finder.find_source(claim, initial_date, final_date, step)
    
    else: 
        initial_date = ""
        final_date = ""
        oldest_aligned_tweet, aligned_tweets = source_finder.find_all(claim, initial_date, final_date)
        top_tweeters = source_finder.get_top_tweeters(aligned_tweets=aligned_tweets, N=N)

    end_time = time.time()
    run_time = end_time - start_time
    print(f"\nExecution time of the Source Finder: {run_time:1f} s\n")

