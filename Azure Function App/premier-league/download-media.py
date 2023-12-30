import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
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

# Remove Words from the caption
rm_words = ["Telegram", "Channel", "Subscribe", "$", "Blockchain", "Promo", "https://t.me"]

def contains_rm_word(text, rm_words):
    text_lower = text.lower() # Convert the text to lowercase for case-insensitive matching
    return any(word.lower() in text_lower for word in rm_words)

# def thread_divider(caption, images):
    # divide images by 4



#************************************ VARIABLES ****************************************************

channel_name = "premier_league_football_news"
# account_name = re.search("AccountName=(.*?);", connection_string).group(1)
telegram_url = f"https://t.me/{channel_name}"
media_ids=[]
api, client = authenticate_twitter()

def post_tweets(caption, media_ids):
    try:
        client.create_tweet(text=caption, media_ids=media_ids)
    except Exception as err:
        print(f"Post Error: {err}")

def find_media(url, message_id):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response_primary = requests.get(url=f"{telegram_url}/{message_id}?embed=1&mode=tme")
    soup_primary = BeautifulSoup(response_primary.content, "html.parser")

    #--------------------- SAVE CAPTION-------------------#
    if bool(soup_primary.find('div', class_='tgme_widget_message_text')) == True:
        message_div = soup_primary.find('div', class_='tgme_widget_message_text')
        caption = str(message_div.get_text())
        if contains_rm_word(caption, rm_words):
            return
        else:
            print(caption)


    if soup_primary.find('div', class_='tgme_widget_message_grouped_wrap'):
        photo_wrap_classes = soup_primary.find_all('a', class_='tgme_widget_message_photo_wrap')
        print(f"Grouped media with {len(photo_wrap_classes)} images")

        for i in range(0, len(photo_wrap_classes)):
            download_url = f"https://t.me/{channel_name}/{message_id+i}?embed=1&mode=tme&single=1"
            download_image(url=download_url, message_id=message_id+i)
            

    elif soup_primary.find('a', class_='tgme_widget_message_photo_wrap') and not soup_primary.find('div', class_='tgme_widget_message_grouped_wrap'):
        download_url = f"https://t.me/{channel_name}/{message_id}?embed=1&mode=tme"
        download_image(url=download_url, message_id=message_id)

    post_tweets(caption, media_ids)



def download_image(url, message_id):
    response_sec = requests.get(url)
    soup_sec = BeautifulSoup(response_sec.content, "html.parser")

    if soup_sec.find('div', class_="tgme_widget_message_error"):
        print("No media")
        return

    image_tag = soup_sec.find('a', class_='tgme_widget_message_photo_wrap')
    image_url = image_tag['style'].split('url(')[1].split(')')[0].strip("'")
    filename = f'{channel_name}-{message_id}.jpg'

    with requests.get(image_url, stream=True) as response:
        with open(filename, 'wb') as img_file:
            for chunk in response.iter_content(chunk_size=8192):
                img_file.write(chunk)
    media_id = api.media_upload(filename=filename).media_id_string
    media_ids.append(media_id)
    return media_ids


find_media(url=telegram_url, message_id=22101)