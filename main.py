'''
In this file, we run the Twitter API for different claims by using the Source_Finder class.
'''

import asyncio 
from source_finder import Source_Finder


# Define the claim and number of tweets we want to retrieve, as well as the maximum number of keywords
claim = "Current studies that conclude climate change is accelerating are invalid because they do not account for natural climate variability."
n_tweets = 20
top_n = 5

# Initialize the class, extract keywords, and form a query
source_finder = Source_Finder(claim, n_tweets)
print("Extracting keywords...")
keywords = source_finder.extract_keywords(top_n)
query = source_finder.build_query(keywords)
print("\nQuery: ", query,"\n")


# Retrieve tweets
tweets, more_tweets = asyncio.run(source_finder.scrape(query=query))
print(f"Number of tweets retrieved: {len(tweets)}")
print(f"Number of extra tweets retrieved: {len(more_tweets) if more_tweets is not None else 0}\n")





