import asyncio
from twikit import Client
from dotenv import load_dotenv
import os


print("Starting scrapper...\n")

load_dotenv()

USERNAME = os.getenv("TWITTER_USERNAME")
EMAIL = os.getenv("TWITTER_EMAIL")
PASSWORD = os.getenv("TWITTER_PASSWORD")

# Initialize client
client = Client("en-US")

mode = "content" # "user" or "content"

async def main():
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD,
        cookies_file="cookies.json",
    )

    if mode == "content":
        query = """(global AND warming AND SNOW AND 50 AND states)"""
        n_tweets = 10
        tweets = await client.search_tweet(query=query, product="Latest", count=n_tweets)
        example_id = "954037043079688192"
        
        ids = []
        counter = 0
        for tweet in tweets:
            counter += 1
            print(f"{counter}. Username: {tweet.user.name} \nDate: {tweet.created_at} \nID: {tweet.id} \n Text:{tweet.text}")
            ids.append(tweet.id)
            print("----------------------------------------")

        print("\n######################\nRetrieving more tweets...\n######################\n")

        n_extra_tweets = 10
        more_tweets = await tweets.next()  # Retrieve more tweets
        for tweet in more_tweets:
            counter += 1
            print(f"{counter}. Username: {tweet.user.name} \nDate: {tweet.created_at} \nID: {tweet.id} \n Text:{tweet.text}")
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
    
    elif mode == "user":
        screen_name = 'exxonmobil'
        n_tweets = 10
        user = await client.get_user_by_screen_name(screen_name)
        user_id = user.id
        tweets = await client.get_user_tweets(user_id=user_id, tweet_type='Tweets', count=n_tweets)
        counter = 0
        for tweet in tweets:
            counter += 1
            print(f"{counter}. Username: {tweet.user.name} \nDate: {tweet.created_at} \nID: {tweet.id} \n Text:{tweet.text}")
            print("----------------------------------------")

        
        print("\n######################\nRetrieving more tweets...\n######################\n")

        n_extra_tweets = 10
        more_tweets = await tweets.next()  # Retrieve more tweets
        for tweet in more_tweets:
            counter += 1
            print(f"{counter}. Username: {tweet.user.name} \nDate: {tweet.created_at} \nID: {tweet.id} \n Text:{tweet.text}")
            print("----------------------------------------")
        

asyncio.run(main())

print("Done")