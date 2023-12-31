import requests
import re
import nltk
nltk.download('punkt')
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

def authenticate_twitter():
    try:
        consumer_key = str(os.getenv('API_KEY'))
        consumer_secret = str(os.getenv('API_KEY_SECRET'))
        access_token = str(os.getenv('ACCESS_TOKEN'))
        access_token_secret = str(os.getenv('ACCESS_TOKEN_SECRET'))
        bearer_token = str(os.getenv('BEARER_TOKEN'))

        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        # Check if Twitter OAuth1UserHandler authentication is successful
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


caption = input("Enter caption: ")

def format_caption(caption):
    thread_text = []

    # Handle single-thread captions
    if len(caption) < 280:
        thread_text.append(caption)
        return thread_text

    # Calculate number of threads
    No_of_threads = len(caption) // 275 + 1

    # Split into sentences and handle long sentences
    sentences = nltk.sent_tokenize(caption)
    for i, sentence in enumerate(sentences):
        if len(sentence) > 275:
            words = sentence.split()
            while words:
                current_line = " ".join(words[:270])
                thread_text.append(current_line)
                words = words[270:]
        else:
            thread_text.append(sentence)

    # Divide sentences into threads of roughly equal length
    threads = []
    current_thread = []
    current_length = 0
    for sentence in thread_text:
        if current_length + len(sentence) + 1 > 275:
            threads.append(current_thread)
            current_thread = []
            current_length = 0
        current_thread.append(sentence)
        current_length += len(sentence) + 1
    threads.append(current_thread)  # Add the last thread

    # If necessary, adjust thread division to match the target number of threads
    while len(threads) > No_of_threads:
        threads[-2].extend(threads[-1])
        threads.pop()

    return threads

def post_to_twitter(threads, media_ids=None):
    """Posts a multi-thread tweet with optional images.

    Args:
        threads: A list of text strings, each representing a thread.
        media_ids: A list of media IDs (optional, for image tweets).
    """

    tweet_id = None
    for i, thread in enumerate(threads):
        if media_ids:
            # Post a tweet with images
            tweet = client.create_tweet(text="\n".join(thread), media_ids=media_ids)
        else:
            # Post a text-only tweet
            tweet = client.create_tweet(text="\n".join(thread), in_reply_to_tweet_id =tweet_id)

        tweet_id = tweet.data['id']
