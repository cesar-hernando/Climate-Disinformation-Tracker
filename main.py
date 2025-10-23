"""
Main script to run the Source Finder using Nitter as the data source.
"""

# Suppress TensorFlow warnings
import os, logging

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from datetime import date
import time
import asyncio
from source_finder_nitter import SourceFinder
from visualization.app import create_app

# Suppress other warnings from imported AI models
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import contractions


##################################################
################ Nitter's domains ################
##################################################

"""
[0] "https://xcancel.com",
[1] "https://nitter.poast.org",
[2] "https://nitter.privacyredirect.com",
[3] "https://lightbrd.com",
[4] "https://nitter.space",
[5] "https://nitter.tiekoetter.com",
[6] "https://nuku.trabun.org",
[7] "https://nitter.kuuro.net",
[8] "https://worldcorrespondents.com"
"""

##################################################
############## Main program ######################
##################################################


async def main():
    # Define the parameters of the search
    claim = "Electric vehicles are actually worse for environment than gas cars"
    claim = contractions.fix(claim)
    max_keywords = 5  # Maximum number of keywords extracted
    synonyms = False  # Whether to use synonyms or not
    n_keywords_dropped = 1  # No advanced search if n_keywords_dropped = 0
    excludes = {"nativeretweets", "replies"}  # Remove replies from here if you want a network analysis (will take longer)
    earliest_k = 10  # Number of earliest aligned tweets to store
    top_n_tweeters = 3  # Top usernames with more tweets about a topic

    mode = 1  # 0 (find source) or 1 (retrieve all)

    model_name = "en_core_web_md"  # Spacy model for contextual synonyms
    top_n_syns = 5  # Number of contextual synonyms to suggest per keyword
    threshold = 0.1  # Similarity threshold for contextual synonyms
    max_syns_per_kw = 2  # Maximum number of synonyms to select per keyword

    start_time = time.time()
    source_finder = SourceFinder(
        max_keywords=max_keywords,
        n_keywords_dropped=n_keywords_dropped,
        excludes=excludes,
    )

    if mode == 0:
        initial_date = "2006-03-21" # yyyy-mm-dd
        final_date = date.today().strftime("%Y-%m-%d")
        step = 1
        by_month = False  # True or False
        if by_month:
            oldest_aligned_tweet, _ = await source_finder.find_source_high_volume(
                claim,
                initial_date,
                final_date,
                step_years=step,
                synonyms=synonyms,
                model_name=model_name,
                top_n_syns=top_n_syns,
                threshold=threshold,
                max_syns_per_kw=max_syns_per_kw,
                dev_mode=True,
            )
        else:
            oldest_aligned_tweet, _, earliest_buf = await source_finder.find_source(
                claim,
                initial_date,
                final_date,
                step,
                synonyms=synonyms,
                model_name=model_name,
                top_n_syns=top_n_syns,
                threshold=threshold,
                max_syns_per_kw=max_syns_per_kw,
                dev_mode=True,
                earliest_k=earliest_k,
            )
        end_time = time.time()
        run_time = end_time - start_time
        print(f"\nExecution time of the Source Finder: {run_time:.2f} s\n")
    else:
        initial_date = "2025-01-01"
        final_date = "2025-10-10"
        filename, tweet_list = await source_finder.find_all(
            claim,
            initial_date,
            final_date,
            verbose=False,
            synonyms=synonyms,
            model_name=model_name,
            top_n_syns=top_n_syns,
            threshold=threshold,
            max_syns_per_kw=max_syns_per_kw,
            dev_mode=True,
        )

        end_time = time.time()
        run_time = end_time - start_time
        print(f"\nExecution time of the Source Finder: {run_time:.2f} s\n")

        if filename is not None:
            # Create and run the visualization app
            app = create_app(filename, claim)
            app.run()

asyncio.run(main())
