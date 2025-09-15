import asyncio
from twikit import Client
from dotenv import load_dotenv
import os
from datetime import datetime

print("Starting scrapper...\n")

load_dotenv()

USERNAME = os.getenv("TWITTER_USERNAME")
EMAIL = os.getenv("TWITTER_EMAIL")
PASSWORD = os.getenv("TWITTER_PASSWORD")

# Initialize client
client = Client("en-US")

async def main():
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD,
        cookies_file="cookies.json",
    )

    query = """global AND warming AND snow AND 50 AND states"""
    n_tweets = 100000
    tweets = await client.search_tweet(query, "Latest", n_tweets)
    example_id = "954037043079688192"
    
    ids = []
    for tweet in tweets:
        print(f"Username: {tweet.user.name} \nDate: {tweet.created_at} \nID: {tweet.id} \n Text:{tweet.text}")
        ids.append(tweet.id)
        print("----------------------------------------")


    print("\nSearching the tweet of ID:", example_id)
    if id in ids:
        print(f"Tweet with ID {example_id} found.")
        index = ids.index(example_id)
        print(f"Date in Twitter format: {tweets[index].created_at}")
        print(f"Username: {tweets[index].user.name}")
        print(f"Text: {tweets[index].text}")
    else:
        print(f"Tweet with ID {example_id} not found.")

asyncio.run(main())

print("Done")