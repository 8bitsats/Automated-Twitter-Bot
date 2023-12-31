import requests
import re
import nltk
nltk.download('punkt')
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString
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


#************************************ VARIABLES ****************************************************

channel_name = "connecttechjobs"
# account_name = re.search("AccountName=(.*?);", connection_string).group(1)
telegram_url = f"https://t.me/{channel_name}"
media_ids=[]
api, client = authenticate_twitter()

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

# tweet=client.create_tweet(text=caption, media_ids=media_ids, in_reply_to_tweet_id=response.data['id'])
def post_tweets(thread_text, media_ids):
    tweet_id = ''

    tweet=client.create_tweet(text=thread_text[0], media_ids=media_ids)

    for i in range(1, 7):
        # 2 or 3 images in a single tweet
        if len(media_ids) >= 2 and len(media_ids) <= 3:
            tweet1 = client.create_tweet(text=f"Thread {i}", media_ids=media_ids)
            print(f"Thread {i} posted")
            break

        # Check for scenario 2: 4 or more images, split and post in threads
        elif i % 4 == 0:
            tweet1 = client.create_tweet(text=f"Thread {i}", media_ids=media_ids, in_reply_to_tweet_id=tweet_id)
            print(f"Thread {i} posted")
            media_ids.clear()

        # Default case: continue adding images to the list
        else:
            continue

    # Check for remaining images and post them if needed
    if media_ids:
        tweet1 = client.create_tweet(text="Remaining images", media_ids=media_ids, in_reply_to_tweet_id=tweet_id)
        print("Remaining images posted")


def find_media(url, message_id):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response_primary = requests.get(url=f"{telegram_url}/{message_id}?embed=1&mode=tme")
    soup_primary = BeautifulSoup(response_primary.content, "html.parser")

    #------------------------- SAVE CAPTION -------------------------#
    if bool(soup_primary.find('div', class_='tgme_widget_message_text')) == True:
        message_div = soup_primary.find('div', class_='tgme_widget_message_text')
        caption = message_div.get_text(strip=True, separator='\n')
        if contains_rm_word(caption, rm_words):
            return

    if soup_primary.find('div', class_='tgme_widget_message_grouped_wrap'):
        photo_wrap_classes = soup_primary.find_all('a', class_='tgme_widget_message_photo_wrap')
        print(f"Grouped media with {len(photo_wrap_classes)} images")

        for i in range(0, len(photo_wrap_classes)):
            download_url = f"https://t.me/{channel_name}/{message_id+i}?embed=1&mode=tme&single=1"
            download_image(url=download_url, message_id=message_id+i)
            

    elif soup_primary.find('a', class_='tgme_widget_message_photo_wrap') and not soup_primary.find('div', class_='tgme_widget_message_grouped_wrap'):
        download_url = f"https://t.me/{channel_name}/{message_id}?embed=1&mode=tme"
        download_image(url=download_url, message_id=message_id)

    formatted_threads = format_caption(caption)
    post_to_twitter(threads=formatted_threads, media_ids=None)
    


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


find_media(url=telegram_url, message_id=492)