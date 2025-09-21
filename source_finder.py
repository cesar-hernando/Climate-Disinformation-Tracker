import asyncio
from twikit import Client
from dotenv import load_dotenv
import os
from keybert import KeyBERT
from itertools import combinations


class Source_Finder:
    def __init__(self, claim, n_tweets):
        self.claim = claim
        self.n_tweets = n_tweets

        load_dotenv()
        self.USERNAME = os.getenv("TWITTER_USERNAME")
        self.EMAIL = os.getenv("TWITTER_EMAIL")
        self.PASSWORD = os.getenv("TWITTER_PASSWORD")

        # Initialize client
        self.client = Client("en-US")
        

    def extract_keywords(self, top_n):
        """Extract keywords from text using KeyBERT"""
        kw_model = KeyBERT(model="AIDA-UPM/mstsb-paraphrase-multilingual-mpnet-base-v2")
        keywords = kw_model.extract_keywords(self.claim, top_n=top_n)
        keywords = [k[0] for k in keywords]
        print(f"Extracted keywords: {keywords}")
        return keywords


    def build_query(self, keywords, n=2):
        """Generate OR-combinations of keywords with AND inside each group"""
        queries = []
        for i in range(len(keywords) - n, len(keywords)):
            for combo in combinations(keywords, i):
                queries.append("(" + " AND ".join(combo) + ")")
        return " OR ".join(queries)
    

    async def scrape(self, mode='claim', verbose=True, query=None, username=None):     
        await self.client.login(
            auth_info_1=self.USERNAME,
            auth_info_2=self.EMAIL,
            password=self.PASSWORD,
            cookies_file="cookies.json",
        )

        print("Starting scraping...")

        # Two modes: search tweets by claim, or search the tweets posted by a specific account
        if mode == "claim":
            tweets = await self.client.search_tweet(query=query, product="Latest", count=self.n_tweets)
            counter = 0
            for tweet in tweets:
                counter += 1
                if verbose:
                    print(f"{counter}. Username: {tweet.user.name} \nDate: {tweet.created_at} \nID: {tweet.id} \n Text:{tweet.text}")
                    print("----------------------------------------")            
        
        elif mode == "username":
            user = await self.client.get_user_by_screen_name(username)
            user_id = user.id
            tweets = await self.client.get_user_tweets(user_id=user_id, tweet_type='Tweets', count=self.n_tweets)
            counter = 0
            for tweet in tweets:
                counter += 1
                if verbose:
                    print(f"{counter}. Username: {tweet.user.name} \nDate: {tweet.created_at} \nID: {tweet.id} \n Text:{tweet.text}")
                    print("----------------------------------------")


        # If not enough tweets are found, we search for more again
        if counter < self.n_tweets:
            if verbose:
                print("\n######################\nRetrieving more tweets...\n######################\n")

            more_tweets = await tweets.next()  # Retrieve more tweets
            for tweet in more_tweets:
                counter += 1
                if verbose:
                    print(f"{counter}. Username: {tweet.user.name} \nDate: {tweet.created_at} \nID: {tweet.id} \n Text:{tweet.text}")
                    print("----------------------------------------")
                if counter == self.n_tweets:
                    break
            
            print("Scraping finished")
            return tweets, more_tweets
        
        else:
            print("Scraping finished")
            return tweets, None
        
