"""
Main script to run the Source Finder using Nitter as the data source.
"""

# Suppress TensorFlow warnings
import os, logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import time
import asyncio
from source_finder_nitter import SourceFinder
#from visualization.app import run_app
import pandas as pd

# Suppress other warnings from imported AI models
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


##################################################
################ Nitter's domains ################
##################################################

'''
[0] "https://xcancel.com",
[1] "https://nitter.poast.org",
[2] "https://nitter.privacyredirect.com",
[3] "https://lightbrd.com",
[4] "https://nitter.space",
[5] "https://nitter.tiekoetter.com",
[6] "https://nuku.trabun.org",
[7] "https://nitter.kuuro.net",
[8] "https://worldcorrespondents.com"
'''

##################################################
############## Main program ######################
##################################################

async def main():
    # Define the parameters of the search
    claim = "Climate change is just caused by natural cycles of the sun"
    domain_index = 5 # Index of the Nitter domain to use, change if one domain is down
    max_keywords = 5 # Maximum number of keywords extracted
    n_keywords_dropped = 1 # No advanced search if n_keywords_dropped = 0
    excludes={"nativeretweets", "replies"}
    top_n_tweeters = 3 # Top usernames with more tweets about a topic

    mode = 0 # 0 (find source) or 1 (retrieve all)

    start_time = time.time()
    source_finder = SourceFinder(domain_index=domain_index, 
                                max_keywords=max_keywords, 
                                n_keywords_dropped=n_keywords_dropped, 
                                excludes=excludes)

    if mode == 0:
        initial_date = "2007-01-01"
        final_date = "2025-01-01"
        step = 1
        by_month = True # True or False
        if by_month:
            oldest_aligned_tweet, _ = await source_finder.find_source_high_volume(claim, initial_date, final_date, step_years=step)
        else:
            oldest_aligned_tweet, _ = await source_finder.find_source(claim, initial_date, final_date, step)
        end_time = time.time()
        run_time = end_time - start_time
        print(f"\nExecution time of the Source Finder: {run_time:.2f} s\n")
    else: 
        initial_date = ""
        final_date = ""
        file_name, tweet_list = await source_finder.find_all(claim, initial_date, final_date)

        end_time = time.time()
        run_time = end_time - start_time
        print(f"\nExecution time of the Source Finder: {run_time:.2f} s\n")

        #if file_name is not None:
        #   # Create and run the visualization app
        #    run_app(file_name, claim, debug=True)

asyncio.run(main())