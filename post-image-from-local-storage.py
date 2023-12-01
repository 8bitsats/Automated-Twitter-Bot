import tweepy
import os
from dotenv import load_dotenv
from platform_authentication import *

# Load environment variables from .env file
load_dotenv()


def post_image_with_caption():
    '''
    Post image from local storage with a custom tweet caption
    '''

    try:
        api, client = authenticate_twitter()
        # Upload image to Twitter.
        media_id = api.media_upload(filename="Path/to/image.jpeg").media_id_string

        # Text to be Tweeted
        text = input("Enter tweet Caption: ")

        # Send Tweet with Text and media ID
        client.create_tweet(text=text, media_ids=[media_id])
        print("Tweeted!")
    except Exception as err:
        print(f"Post Error: {err}")


# post_image_with_caption()
