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
import time

class SourceFinder:
    def __init__(self, top_n=5, n=2, excludes={"nativeretweets", "replies"}):
        self.top_n = top_n
        self.n = n
        self.excludes = excludes

    def run(self, claim, filename, initial_date="", final_date=""):
        query_generator = QueryGenerator(claim)
        query = query_generator.build_query(top_n=self.top_n, n=self.n)
        scraper = ScraperNitter()
        scraper.get_tweets(query=query, 
                           since=initial_date, 
                           until=final_date, 
                           excludes={"nativeretweets", "replies"}, 
                           filename=filename)
        print(f"Scraping completed. Tweets saved to {filename}.")


if __name__ == "__main__":
    # Define the parameters of the search
    claim = "Electric vehicles are actually worse for environment than gas cars"
    initial_date = "2024-05-01"
    final_date = "2024-10-31"
    n = 0 # No advanced search
    filename = f'Electric_cars_worse_n_{n}_{initial_date}_to_{final_date}.csv'
    top_n = 5
    excludes={"nativeretweets", "replies"}

    # Execute the source finder tool
    start_time = time.time()
    source_finder = SourceFinder(top_n=top_n, n=n, excludes=excludes)
    source_finder.run(claim, filename, initial_date, final_date)
    end_time = time.time()
    run_time = end_time - start_time
    print(f"Execution time of the Source Finder: {run_time} s")


