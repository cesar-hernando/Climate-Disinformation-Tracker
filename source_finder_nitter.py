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

import time
from datetime import date
from collections import Counter
import asyncio
import os
import pandas as pd
from datetime import date as _date

from scrapper_nitter import ScraperNitter
from query_generator import QueryGenerator
from alignment import AlignmentModel
from query_builder_synonyms import SynonymQueryBuilder


class SourceFinder:
    def __init__(self, domain_index=5, max_keywords=5, n_keywords_dropped=2, excludes={"nativeretweets", "replies"}, batch_size=4):
        self.domain_index = domain_index # Index of the Nitter domain to use, change if one domain is down
        self.max_keywords = max_keywords # Maximum number of keywords extracted by KeyBert
        self.n_keywords_dropped = n_keywords_dropped # Number of keywords dropped per clause
        self.excludes = excludes
        self.batch_size = batch_size
    

    @staticmethod
    def print_tweet(tweet, separator=80):
        """
        Prints a tweet with all its fields in a nice way to visualize it.
        """

        print("-" * separator)
        for key, value in tweet.items():
            # replace underscore w spaces
            field_name = key.replace("_", " ").capitalize()
            
            # newline if too long
            if isinstance(value, str) and len(value) > 80:
                print(f"{field_name}:\n{value}")
            else:
                print(f"{field_name}: {value}")
        print("-" * separator)

    def print_tweet_with_alignment(self, t: dict):
        """Print one tweet and show its alignment if present."""
        self.print_tweet(t)
        if "alignment" in t:
            print(f"Alignment: {t['alignment']}\n")

    def print_earliest_list(self, tweets: list, limit: int | None = None):
        """Pretty-print the earliest_k list (oldest → newer)."""
        if not tweets:
            print("No earliest tweets collected.")
            return
        print(f"\n=== Earliest tweets (showing {len(tweets) if not limit else min(len(tweets), limit)}/{len(tweets)}) ===\n")
        n = len(tweets) if limit is None else min(limit, len(tweets))
        for i in range(n):
            print(f"[{i+1}] -----------------------------------------------")
            self.print_tweet_with_alignment(tweets[i])


    def predict_alignment(self, claim, tweets_list, filename):
        """
        Saves the tweets along with their alignment to a CSV file.
        """
        alignment_model = AlignmentModel()
        print(f"Predicting alignment for {len(tweets_list)} tweets...")
        alignment_list = alignment_model.batch_predict(claim, tweets_list, batch_size=self.batch_size)

        if not tweets_list or not alignment_list or len(tweets_list) != len(alignment_list):
            print("No tweets or alignment data to save, or lengths do not match.")
            return

        # Add alignment to each tweet
        for tweet, alignment in zip(tweets_list, alignment_list):
            tweet['alignment'] = alignment

        df = pd.DataFrame(tweets_list)
        df.to_csv(filename, index=False, encoding='utf-8')

        print(f"Tweets with alignment saved to {filename}.")
        return df    
    

    async def find_all(self, claim, initial_date="", final_date="", verbose=False, synonyms=False, 
                       model_name="en_core_web_md", top_n_syns=5, threshold=0.1, max_syns_per_kw=2, data_dir="data/"):
        """
        Transforms a claim into a query for advanced search, retrieves tweets using Nitter, selects the
        tweets that align with the original claim, and obtains the oldest.
        """
        if synonyms:
            query_builder = SynonymQueryBuilder(
                sentence=claim, 
                max_keywords=self.max_keywords, 
                n_keywords_dropped=self.n_keywords_dropped,
                model_name=model_name,
                top_n_syns=top_n_syns,
                threshold=threshold,
                max_syns_per_kw=max_syns_per_kw
            )
            keywords = query_builder.keywords
            query = query_builder.run()
        else:
            query_generator = QueryGenerator(claim)
            keywords = query_generator.extract_keywords(max_keywords=self.max_keywords)
            query = query_generator.build_query(n_keywords_dropped=self.n_keywords_dropped, keywords=keywords)

        print(f"\nGenerated Boolean Query:\n{query}\n")

        if initial_date == "":
            initial_date = "2006-03-21" # Beginning of Twitter

        if final_date == "":
            final_date = date.today().strftime("%Y-%m-%d")

        ind_syns = "with_syns" if synonyms else ""
        filename = data_dir + "_".join(keywords) + f'_kpc_{self.max_keywords - self.n_keywords_dropped}_{initial_date}_to_{final_date}_{ind_syns}.csv' # kpc stands for keywords per clause

        if os.path.exists(filename):
            print(f"\nFile {filename} already exists.\n")
            return filename, None
        
        async with ScraperNitter(domain_index=self.domain_index) as scraper:
            print(f"Scraping url: {scraper.domain + scraper._get_search_url(query, initial_date, final_date, excludes=self.excludes)}")
            tweets_list = await scraper.get_tweets(
                query=query, 
                since=initial_date, 
                until=final_date, 
                save_csv=False,
                excludes=self.excludes, 
                verbose=verbose,
                filename=filename)
        
            if tweets_list:
                print(f"\nScraping completed. Found {len(tweets_list)} tweets.\n")
                tweets_list = self.predict_alignment(claim, tweets_list, filename)
                df = pd.DataFrame(tweets_list)

                return filename, df
            else:
                print(f"\nNo tweets were found.\n")
                return None, None

    async def find_source(self, claim, initial_date="", final_date="", step=1, synonyms=True, model_name="en_core_web_md", 
                          top_n_syns=5, threshold=0.1, max_syns_per_kw=2, earliest_k: int = 0):
        """
        Find the earliest entailing tweet ('source').
        Additionally, if earliest_k > 0, also collect up to earliest_k earliest tweets
        (any alignment) seen while scanning forward in time. We assume get_tweets returns
        newest→oldest, so we simply reverse() each batch to get oldest→newest.

        NEW: even after the source is found, keep scanning forward until earliest_buf is full.
        """
        
        if synonyms:
            query_builder = SynonymQueryBuilder(
                sentence=claim,
                max_keywords=self.max_keywords,
                n_keywords_dropped=self.n_keywords_dropped,
                model_name=model_name,
                top_n_syns=top_n_syns,
                threshold=threshold,
                max_syns_per_kw=max_syns_per_kw
            )
            keywords = query_builder.keywords
            query = query_builder.run()
        else:
            query_generator = QueryGenerator(claim)
            keywords = query_generator.extract_keywords(max_keywords=self.max_keywords)
            query = query_generator.build_query(
                n_keywords_dropped=self.n_keywords_dropped,
                keywords=keywords
            )

        print(f"\nGenerated Boolean Query:\n{query}\n")

        if initial_date == "":
            initial_date = "2006-03-21" # Beginning of Twitter
        if final_date == "":
            final_date = _date.today().strftime("%Y-%m-%d")

        alignment_model = AlignmentModel()
        earliest_buf: list[dict] = []

        # var to store src bc don't want to ret immediately
        source_tweet = None
        source_aligned_batch = None  

        async with ScraperNitter(domain_index=self.domain_index) as scraper:
            initial_year = int(initial_date[:4])
            final_year   = int(final_date[:4])

            start_y = initial_year
            end_y   = min(final_year + 1, start_y + step)

            while start_y <= final_year:
                # if buffer is full, break
                if earliest_k > 0 and len(earliest_buf) >= earliest_k and source_tweet is not None:
                    break

                since = f"{start_y}{initial_date[4:]}"
                until = f"{end_y}{initial_date[4:]}"
                print(f"\nRetrieving tweets from {since} to {until}...")

                tweets = await scraper.get_tweets(
                    query=query,
                    since=since,
                    until=until,
                    excludes=self.excludes,
                    save_csv=False
                )

                if not tweets:
                    print("No tweets were found.")
                    # advance window
                    start_y += step
                    end_y = min(final_year + 1, start_y + step)
                    continue

                print(f"{len(tweets)} tweets were found.")

                tweets.reverse()

                # as long as buffer is not full
                if earliest_k > 0 and len(earliest_buf) < earliest_k:
                    need = earliest_k - len(earliest_buf)
                    # take as many as needed to fill buffer only
                    take = tweets[:need]

                    # label whats been taken
                    labels = alignment_model.batch_predict(claim, take, batch_size=self.batch_size)
                    for tw, lab in zip(take, labels):
                        tw["alignment"] = lab

                    earliest_buf.extend(take)

                    # if src hasnt been found yet, check for entailments
                    if source_tweet is None:
                        entailing_now = [t for t in take if t.get("alignment") == "entails"]
                        if entailing_now:
                            source_tweet = entailing_now[0]  # take the earliest in this slice
                            source_tweet["is_source"] = True
                            source_tweet["side"] = "source"
                            print("\nOldest aligned tweet found (from earliest slice):")
                            self.print_tweet(source_tweet)

                # do normal src finding once buffer is full
                if source_tweet is None:
                    print("None of the earliest slice entails (or buffer not full yet). Checking alignment on full batch...")
                    aligned_tweets = alignment_model.batch_filter_tweets(
                        claim,
                        tweets,
                        batch_size=self.batch_size
                    )
                    if aligned_tweets:
                        found_here = alignment_model.find_first(aligned_tweets)
                        found_here["is_source"] = True
                        found_here["side"] = "source"
                        source_tweet = found_here
                        source_aligned_batch = aligned_tweets
                        print("\nOldest aligned tweet:")
                        self.print_tweet(source_tweet)
                    else:
                        print("None of the tweets found are aligned with the original claim.")

                start_y += step
                end_y = min(final_year + 1, start_y + step)


        if source_tweet is None:
            print("\nNo aligned tweets were found between the dates provided.\n")
            if earliest_k > 0:
                return None, None, earliest_buf
            return None, None

        if earliest_k > 0:
            return source_tweet, (source_aligned_batch or [source_tweet]), earliest_buf
        else:
            return source_tweet, (source_aligned_batch or [source_tweet])


    async def find_source_high_volume(self, claim, initial_date="", final_date="", step_years=1, synonyms=True, 
                                     model_name="en_core_web_md", top_n_syns=5, threshold=0.1, max_syns_per_kw=2):
        """
        Similar to find_source, but optimized for high tweet volumes.
        For each year range (step_years), it first checks if any tweets exist.
        If tweets exist, it retrieves tweets month by month and checks alignment.
        Stops immediately when aligned tweets are found; otherwise moves to next year range.
        """
        if synonyms:
            query_builder = SynonymQueryBuilder(
                sentence=claim, 
                max_keywords=self.max_keywords, 
                n_keywords_dropped=self.n_keywords_dropped,
                model_name=model_name,
                top_n_syns=top_n_syns,
                threshold=threshold,
                max_syns_per_kw=max_syns_per_kw
            )
            query = query_builder.run()
        else:
            query_generator = QueryGenerator(claim)
            keywords = query_generator.extract_keywords(max_keywords=self.max_keywords)
            query = query_generator.build_query(n_keywords_dropped=self.n_keywords_dropped, keywords=keywords)

        print(f"\nGenerated Boolean Query:\n{query}\n")

        if initial_date == "":
            initial_date = "2006-03-21"  # Beginning of Twitter

        if final_date == "":
            final_date = date.today().strftime("%Y-%m-%d")

        # Extract year from date
        initial_year = int(initial_date[:4])
        final_year = int(final_date[:4])

        prov_initial_year = initial_year
        prov_final_year = initial_year + step_years

        alignment_model = AlignmentModel()

        async with ScraperNitter(domain_index=self.domain_index) as scraper:
            # Loop over each year range
            while prov_final_year <= (final_year + 1):
                prov_initial_date = str(prov_initial_year) + initial_date[4:]
                prov_final_date = str(prov_final_year) + initial_date[4:]

                print(f"\nSearching tweets from {prov_initial_date} to {prov_final_date}...")

                # Quick check — are there tweets in this range at all?
                tweets_found = await scraper.check_tweets_exist(
                    query=query,
                    since=prov_initial_date,
                    until=prov_final_date,
                    excludes=self.excludes,
                )

                if not tweets_found:
                    print("No tweets found in this year range.")
                    prov_initial_year += step_years
                    prov_final_year += step_years
                    continue

                print("Tweets exist. Checking month by month...")

                # Loop month by month in this year range
                current_year = prov_initial_year
                current_month = 1  # Start from January
                while current_year < prov_final_year or (current_year == prov_final_year and current_month <= 12):
                    prov_month_start = f"{current_year}-{current_month:02d}-01"

                    # Calculate next month
                    if current_month == 12:
                        next_month = 1
                        next_year = current_year + 1
                    else:
                        next_month = current_month + 1
                        next_year = current_year

                    prov_month_end = f"{next_year}-{next_month:02d}-01"
                    print(f"  Retrieving tweets from {prov_month_start} to {prov_month_end}...")

                    # Get tweets for this month
                    month_tweets = await scraper.get_tweets(
                        query=query,
                        since=prov_month_start,
                        until=prov_month_end,
                        excludes=self.excludes,
                        save_csv=False,
                    )

                    if not month_tweets:
                        print("    No tweets this month.")
                        current_year, current_month = next_year, next_month
                        continue

                    print(f"    Found {len(month_tweets)} tweets. Checking alignment...")

                    # Check alignment immediately
                    aligned_tweets = alignment_model.batch_filter_tweets(
                        claim,
                        month_tweets,
                        batch_size=self.batch_size
                    )

                    if aligned_tweets:
                        oldest_aligned_tweet = alignment_model.find_first(aligned_tweets)
                        print("\nOldest aligned tweet found:")
                        self.print_tweet(oldest_aligned_tweet)
                        return oldest_aligned_tweet, aligned_tweets

                    print("    No aligned tweets this month.")
                    current_year, current_month = next_year, next_month

                print("No aligned tweets found in this year range.")
                prov_initial_year += step_years
                prov_final_year += step_years

        print("\nNo aligned tweets were found between the dates provided.\n")
        return None, None
       
            

    @staticmethod
    def get_top_tweeters(aligned_tweets, top_n_tweeters=5):
        """
        Returns the top usernames with most tweets, the number of tweets, and their tweets.
        """
        if not aligned_tweets:
            return []

        # Count tweets per user
        users = [tweet['user'] for tweet in aligned_tweets]
        user_counts = Counter(users)

        # Get top N users
        top_users = user_counts.most_common(top_n_tweeters)

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

# pretty print -------------------------------------------------
if __name__ == "__main__":

    async def main():
        # params (same as before)
        claim = "The earth is surrounded by an ice wall."
        max_keywords = 5
        n_keywords_dropped = 1
        excludes = {"nativeretweets", "replies"}
        batch_size = 4
        mode = 0  # 0=find source (+ print earliest list), 1=retrieve all

        start_time = time.time()
        source_finder = SourceFinder(
            max_keywords=max_keywords,
            n_keywords_dropped=n_keywords_dropped,
            excludes=excludes,
            batch_size=batch_size
        )

        if mode == 0:
            initial_date = "2025-04-29"
            final_date   = "2025-10-08"
            step = 1

            source, aligned, earliest = await source_finder.find_source(
                claim,
                initial_date=initial_date,
                final_date=final_date,
                step=step,
                synonyms=True,
                earliest_k=150,         # <<< just this
            )

            # print source (if found)
            if source:
                print("\n=== SOURCE (oldest entailing) ===")
                # SourceFinder.print_tweet(source_finder, source)
                SourceFinder.print_tweet(source)

            for i, t in enumerate(earliest, 1):
                print(f"[{i}] -----------------------------------------------")
                #SourceFinder.print_tweet(source_finder, t)
                SourceFinder.print_tweet(t)
                if "alignment" in t:
                    print(f"Alignment: {t['alignment']}\n")

        else:
            # unchanged find_all path
            initial_date = ""
            final_date   = "2025-10-08"
            filename, tweet_list = await source_finder.find_all(claim, initial_date, final_date)
            print(f"{len(tweet_list)} Tweets saved in {filename}")

        end_time = time.time()
        print(f"\nExecution time of the Source Finder: {end_time - start_time:.2f} s\n")

    asyncio.run(main())
