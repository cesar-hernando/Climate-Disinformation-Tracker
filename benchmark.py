"""
Benchmarking script to evaluate the performance of the SourceFinder class
on a list of claims. This version appends new results and skips already processed claims.
"""

# Suppress TensorFlow warnings
import os
import logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
tf.get_logger().setLevel(logging.ERROR)

import csv
import asyncio
import time
from source_finder_nitter import SourceFinder

# Suppress other warnings from imported AI models
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


##################################################
################# PARAMETERS #####################
##################################################

# domain_index = 5                          # Index of the Nitter domain to use, change if one domain is down
max_keywords = 5                          # Maximum number of keywords extracted
n_keywords_dropped = 1                    # No advanced search if n_keywords_dropped = 0
excludes = {"nativeretweets", "replies"}  # Filters to exclude from search
initial_date = "2007-01-01"               # Start date for searching tweets
final_date = "2025-01-01"                 # End date for searching tweets
step = 1                                  # Step in years for searching tweets in find_source mode
filename = "benchmark_results_bymonth.csv"        # Output CSV file for results
by_month = True                        # Whether to use monthly steps in high volume mode


##################################################
################### FUNCTIONS ####################
##################################################

async def process_claim(claim, writer):
    """Asynchronously process a single claim and record results."""
    print(f"\nProcessing claim: {claim}")
    start_time = time.time()

    source_finder = SourceFinder(
        max_keywords=max_keywords,
        n_keywords_dropped=n_keywords_dropped,
        excludes=excludes,
    )

    try:
        if by_month:
            oldest_aligned_tweet, _ = await source_finder.find_source_high_volume(
                claim, initial_date, final_date, step_years=step
            )
        else:
            oldest_aligned_tweet, _ = await source_finder.find_source(
                claim, initial_date, final_date, step
            )

        tweet_found = oldest_aligned_tweet is not None
        tweet_text = oldest_aligned_tweet["text"] if tweet_found else "No tweet found"
        tweet_date = oldest_aligned_tweet["created_at_datetime"] if tweet_found else "-"
        tweet_user = oldest_aligned_tweet["user"] if tweet_found else "-"
        tweet_link = oldest_aligned_tweet["link"] if tweet_found else "-"
        tweet_comments = oldest_aligned_tweet["comments"] if tweet_found else "-"
        tweet_retweets = oldest_aligned_tweet["retweets"] if tweet_found else "-"
        tweet_likes = oldest_aligned_tweet["likes"] if tweet_found else "-"
        tweet_quotes = oldest_aligned_tweet["quotes"] if tweet_found else "-"

    except Exception as e:
        print(f"Error processing claim '{claim}': {e}")
        tweet_text = f"Error: {e}"
        tweet_date = "-"
        tweet_user = "-"
        tweet_link = "-"
        tweet_comments = "-"
        tweet_retweets = "-"
        tweet_likes = "-"
        tweet_quotes = "-"

    end_time = time.time()
    run_time = end_time - start_time
    print(f"\nExecution time of the Source Finder: {run_time:.2f} s\n")

    # Save results to CSV
    writer.writerow([claim, f"{run_time:.2f}", tweet_text, tweet_date, tweet_user, 
                     tweet_link, tweet_comments, tweet_retweets, tweet_likes, tweet_quotes])
    print("Results saved.")


##################################################
##################### MAIN #######################
##################################################

async def main():
    # Read claims from list_of_claims.txt
    with open("list_of_claims.txt", "r", encoding="utf-8") as f:
        all_claims = [line.strip() for line in f if line.strip()]

    # Read already processed claims from existing CSV (if any)
    processed_claims = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if row:
                    processed_claims.add(row[0])

    # Determine which claims still need to be processed
    pending_claims = [c for c in all_claims if c not in processed_claims]

    if not pending_claims:
        print("\n All claims have already been processed.")
        return

    print(f"\n{len(pending_claims)} new claims to process...\n")

    # Open CSV in append mode
    write_header = not os.path.exists(filename) or os.path.getsize(filename) == 0
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Claim", "Execution time (s)", "Tweet found", "Date", "Username", 
                             "Link", "Comments", "Retweets", "Likes", "Quotes"])

        # Process pending claims sequentially
        for claim in pending_claims:
            await process_claim(claim, writer)

    print(f"\nBenchmarking completed. Results saved to {filename}\n")


if __name__ == "__main__":
    asyncio.run(main())
