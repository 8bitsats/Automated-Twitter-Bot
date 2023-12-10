import tweepy

consumer_key = "3CgqYXpcuKhGCD1cBi7oFzvWL"
consumer_secret = "K54ccQQJRIvk2sg4DupBoJBZwYYW8EVkHnZSDwMfMxFKtfdJ5m"
access_token = "1483479711510638601-Y03ezxn1ZMDQOM49mYA0n7cgGPkea7"
access_token_secret = "yCdbMSmCd1MZPpzIFqhTrztmM7CUjOG1i0AC3l8T3HE5O"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAN0%2BnQEAAAAA81QQpJe5LTxTA1zjAiYfhh2rFs0%3DExWI4gxQcObZjFk1gmBabmCXxqyeZWsrfs1DZUYafJWPPRQfOl"


auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Check if Twitter authentication is successful
user = api.verify_credentials()
print(f"User {user.screen_name} Authenticated !")

# V2 Twitter API Authentication
client = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    wait_on_rate_limit=True,
    )


media_ids = []
TWEET_TEXT = 'some tweet caption'

for i in range(1,5): #Set 1 to 4 images (exemple with 2)
    IMAGE_PATH = f'{i}.jpg'
    # file = open(IMAGE_PATH, 'rb')
    # data = file.read()
    media_id = api.media_upload(filename=IMAGE_PATH).media_id_string
    media_ids.append(media_id)

print(media_ids)
client.create_tweet(text=TWEET_TEXT, media_ids=media_ids)
