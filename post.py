import tweepy
from ai_tweet import *

def post_tweet(tweet):
    api.update_status(tweet)

def like_and_reply(tweet_id, reply_text):
    api.create_favorite(tweet_id)
    api.update_status(status=reply_text, in_reply_to_status_id=tweet_id)
