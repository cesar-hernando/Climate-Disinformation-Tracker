'''
In this file, we compare different datasets.

First, we check that datasets with synonyms must include all tweets from 
datasets without synonyms when both are generated with the same parameters.

Secondly, we analyze the overlap in usernames between datasets to try to
find potential disinformation spreaders.
'''

import pandas as pd
from pathlib import Path
from collections import Counter

def check_overlap(A, B):
    links_A = set(A['link'].tolist())
    links_B = set(B['link'].tolist())
            
    A_and_B = links_A & links_B
    A_not_in_B = links_A - links_B
    B_not_in_A = links_B - links_A

    print(f"Total tweets in dataset A: {len(links_A)}")
    print(f"Total tweets in dataset B: {len(links_B)}")
    if len(A_not_in_B) == 0:
        print("All tweets in dataset A are present in dataset B.")
    else:
        print(f"{len(A_not_in_B)} tweets in dataset A are missing in dataset B.")
    
    if len(B_not_in_A) == 0:
        print("All tweets in dataset B are present in dataset A.")
    else:
        print(f"{len(B_not_in_A)} tweets in dataset B are missing in dataset A.")
    
    print(f"Number of tweets in both datasets: {len(A_and_B)}\n")


def top_usernames_across_datasets(datasets, top_n=10):
    """
    Finds top usernames across multiple datasets,
    avoiding double-counting the same tweet (same 'link' or 'id').
    """
    # Combine all datasets and deduplicate by tweet link or ID
    combined_df = pd.concat(datasets, ignore_index=True)

    # Pick a column to identify unique tweets
    if 'link' in combined_df.columns:
        unique_df = combined_df.drop_duplicates(subset='link')
    elif 'id' in combined_df.columns:
        unique_df = combined_df.drop_duplicates(subset='id')
    else:
        print("No 'link' or 'id' column found; duplicates across datasets may remain.")
        unique_df = combined_df

    # Detect username column
    if 'user' in unique_df.columns:
        username_col = 'user'
    elif 'username' in unique_df.columns:
        username_col = 'username'
    else:
        raise KeyError("No 'user' or 'username' column found in datasets.")

    # Count usernames
    counter = Counter(unique_df[username_col].dropna().tolist())
    most_common = counter.most_common(top_n)

    # Calculate in how many datasets each username appears
    username_counters = []
    for data in datasets:
        col = 'user' if 'user' in data.columns else 'username'
        username_counters.append(Counter(data[col].dropna().tolist()))

    print(f"Top {top_n} usernames across datasets (unique tweets only):")
    for i, (username, count) in enumerate(most_common, start=1):
        dataset_count = sum(1 for c in username_counters if username in c)
        print(f"{i}. Username: {username}, Unique Tweets: {count}, Datasets Appeared In: {dataset_count}")



if __name__ == "__main__":

    mode = "top_usernames"  # "analyze_overlap" or "top_usernames"
    
    if mode == "analyze_overlap":
        with_syns = pd.read_csv("data/electric_gas_worse_environment_cars_kpc_4_2006-03-21_to_2025-10-10_with_syns.csv")
        without_syns = pd.read_csv("data/electric_gas_worse_environment_cars_kpc_4_2006-03-21_to_2025-10-10_.csv")
        print("\nChecking overlap between datasets with synonyms (A) and without synonyms (B):\n")
        check_overlap(with_syns, without_syns)
        
    elif mode == "top_usernames":
        folder_path_results = Path("./results")
        datasets_results = [pd.read_csv(f) for f in folder_path_results.glob("*.csv")]
        folder_path_data = Path("./data")
        datasets_data = [pd.read_csv(f) for f in folder_path_data.glob("*.csv")]
        datasets = datasets_results + datasets_data
        top_usernames_across_datasets(datasets, top_n=20)
