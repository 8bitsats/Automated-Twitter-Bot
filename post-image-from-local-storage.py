import tweepy
# import openai
# import telegram
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
        bearer_token = str(os.getenv('BEARER_TOKEN'))

        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        # Check if Twitter authentication is successful
        user = api.verify_credentials()
        print(f"Twitter authentication successful. User: {user.screen_name}")
        
        # V2 Twitter API Authentication
        client = tweepy.Client(
            bearer_token,
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
            wait_on_rate_limit=True,
        )
        return api, client

    except tweepy.TweepyException as e:
        print(f"Twitter authentication failed: {e}")
        return None


def post_image_with_caption():
    api, client = authenticate_twitter()
    # Upload image to Twitter.
    media_id = api.media_upload(filename="Path/to/image.jpeg").media_id_string
    print(media_id)

    # Text to be Tweeted
    text = "Hello Twitter!"

    # Send Tweet with Text and media ID
    client.create_tweet(text=text, media_ids=[media_id])
    print("Tweeted!")


# post_image_with_caption()
