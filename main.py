"""
Main script to run the Source Finder using Nitter as the data source.
"""

# Suppress TensorFlow warnings
#import os, logging
#os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

#import tensorflow as tf
#tf.get_logger().setLevel(logging.ERROR)

import time
from source_finder_nitter import SourceFinder

# Suppress other warnings from imported AI models
#import warnings
#warnings.filterwarnings("ignore", category=UserWarning)
#warnings.filterwarnings("ignore", category=DeprecationWarning)


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

# Define the parameters of the search
domain_index = 5 # Index of the Nitter domain to use, change if one domain is down
claim = "Climate change is just a natural cycle - the Earth has always warmed and cooled"
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
    oldest_aligned_tweet, aligned_tweets = source_finder.find_source(claim, initial_date, final_date, step)
else: 
    initial_date = ""
    final_date = ""
    oldest_aligned_tweet, aligned_tweets = source_finder.find_all(claim, initial_date, final_date)
    top_tweeters = source_finder.get_top_tweeters(aligned_tweets=aligned_tweets, top_n_tweeters=top_n_tweeters)

end_time = time.time()
run_time = end_time - start_time
print(f"\nExecution time of the Source Finder: {run_time:.2f} s\n")