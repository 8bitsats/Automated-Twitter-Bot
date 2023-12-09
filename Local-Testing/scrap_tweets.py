import tweepy

# consumer_key = ""
# consumer_secret = ""
# access_token = ""
# access_token_secret = ""
# bearer_token = ""


# auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)
# api = tweepy.API(auth, wait_on_rate_limit=True)

# # Check if Twitter authentication is successful
# user = api.verify_credentials()
# print(f"User {user.screen_name} Authenticated !")

# # V2 Twitter API Authentication
# client = tweepy.Client(
#     bearer_token,
#     consumer_key,
#     consumer_secret,
#     access_token,
#     access_token_secret,
#     wait_on_rate_limit=True,
#     )

excluded_names = ['Telegram', 'telegram', 'BET']


#************************************ VARIABLES ****************************************************
log_values = []
channel_name = "mqquotes"
message_id = random.choice(range(11341,16142))
account_name = re.search("AccountName=(.*?);", connection_string).group(1)
telegram_download_url = f"https://t.me/{channel_name}/{message_id}?embed=1&mode=tme"
response = requests.get(url=telegram_download_url)
soup = BeautifulSoup(response.content, "html.parser")
error = soup.find('div', class_="tgme_widget_message_error")
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
filename = '' # Dynamic file name to store the new blob to be downloaded
log_values.extend([current_time, channel_name, message_id])


# media_ids = ''

# for i in range(2): #Set 1 to 4 images (exemple with 2)
#     TWEET_TEXT = 'some tweet text'
#     IMAGE_PATH = f'{i}.jpg'
#     file = open(IMAGE_PATH, 'rb')
#     data = file.read()
#     r = api.request('media/upload', None, {'media': data})
#     print('UPLOAD MEDIA SUCCESS' if r.status_code == 200 else 'UPLOAD MEDIA FAILURE')


#     if r.status_code == 200:
#         if i == 0:
#             media_ids += str(r.json()['media_id'])
#         else:
#             media_ids = media_ids + ',' + str(r.json()['media_id'])

# #POST IMAGES
# r = api.request('statuses/update', {'status':TWEET_TEXT, 'media_ids':media_ids})
# print('UPDATE STATUS SUCCESS' if r.status_code == 200 else 'UPDATE STATUS FAILURE')