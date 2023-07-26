import tweepy
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def authenticate_twitter():
    try:
        consumer_key = str(os.getenv('CONSUMER_KEY'))
        consumer_secret = str(os.getenv('API_SECRET_KEY'))
        access_token = str(os.getenv('ACCESS_TOKEN'))
        access_token_secret = str(os.getenv('ACCESS_TOKEN_SECRET'))

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        # Check if Twitter authentication is successful
        user = api.verify_credentials()
        print(f"Twitter authentication successful. User: {user.screen_name}")
        return api

    except tweepy.TweepyException as e:
        print(f"Twitter authentication failed: {e}")
        return None


def authenticate_openai():
    openai.api_key = str(os.getenv("OPENAI_API_KEY"))

    try:
        response = openai.Completion.create(engine="text-davinci-002", prompt="Testing authentication.")
        print("OpenAI authentication successful.")
        return True

    except Exception as e:
        print(f"OpenAI authentication failed: {e}")
        return False

