from auth import *
from post import post_tweet


if __name__ == "__main__":
    # Authenticate with Twitter and OpenAI
    twitter_api = authenticate_twitter()
    openai_authenticated = authenticate_openai()

    # Continue with the rest of the code if both authentications are successful
    if twitter_api and openai_authenticated:
        post_tweet(tweet)
        # parent_tweet_id = api.user_timeline(count=1)[0].id
        # comment_id = api.update_status(status="Comment on the tweet", in_reply_to_status_id=parent_tweet_id).id
        # reply_prompt = "Reply to the comment."
        # reply_text = generate_reply(reply_prompt)
        # like_and_reply(comment_id, reply_text)
    else:
        print("Authentication failed. Please check your API keys and tokens.")