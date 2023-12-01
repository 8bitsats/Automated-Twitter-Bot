import tweepy
from auth import authenticate_twitter

def get_tweets(api, username, year):
    tweets = []
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended").items():
        if tweet.created_at.year == year:
            tweets.append(tweet.full_text)
        elif tweet.created_at < year:
            break
    return tweets

twitter_api = authenticate_twitter()

if twitter_api:
    username = '@iammemeloper'
    year = 2016

    user_tweets = get_tweets(twitter_api, username=username, year=year)
    for idx, tweet in enumerate(user_tweets, start=1):
        print(f"Tweet {idx}: {tweet}\n")

else:
    print("Authentication failed")

