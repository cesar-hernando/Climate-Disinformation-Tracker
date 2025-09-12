import asyncio
from twikit import Client
from dotenv import load_dotenv
import os

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

    # Search for 5 tweets containing the keyword "climate"
    tweets = await client.search_tweet("climate", "Latest", 5)

    for tweet in tweets:
        print(tweet.user.name, "\n", tweet.text, "\n", tweet.created_at)
        print("----------------------------------------")


asyncio.run(main())

print("Done")