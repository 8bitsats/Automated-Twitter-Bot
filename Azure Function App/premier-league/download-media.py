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
# rm_words = []

def contains_rm_word(text, rm_words):
    text_lower = text.lower() # Convert the text to lowercase for case-insensitive matching
    return any(word.lower() in text_lower for word in rm_words)


#************************************ VARIABLES ****************************************************

channel_name = "premier_league_football_news"
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

    # Tokenize sentences
    sentences = nltk.sent_tokenize(caption)
    formatted_caption = "\n".join(sentences)

    No_of_threads = len(formatted_caption) // 270 + 1

    # Split the caption into threads based on the character limit
    words = formatted_caption.split()
    current_thread = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > 270:
            # Move to the next thread if adding the word would exceed the limit
            thread_text.append(" ".join(current_thread))
            current_thread = [word]
            current_length = len(word)
        else:
            current_thread.append(word)
            current_length += len(word) + 1

    if current_thread:
        thread_text.append(" ".join(current_thread))

    # Ensure the correct number of threads is created
    while len(thread_text) > No_of_threads:
        thread_text[-2] += " " + thread_text[-1]
        thread_text.pop()

    # Print threads and character counts
    for i, thread in enumerate(thread_text):
        total_chars = len(thread)
        print('*' * 50)
        print(f"Thread {i + 1} (Total Characters = {total_chars}):\n" + thread)

    return thread_text

def post_to_twitter(threads, media_ids_arrays):
    """Posts a multi-thread tweet with optional images.

    Args:
        threads: A list of text strings, each representing a thread.
        media_ids: A list of media IDs (optional, for image tweets).
    """
    if len(threads) >= len(media_ids_arrays):
        No_of_threads = len(threads)
    else:
        No_of_threads = len(media_ids_arrays)

    tweet_id = None
    # Zip threads and media_ids_arrays together
    for i in range(max(len(threads), len(media_ids_arrays))):
        thread = threads[i] if i < len(threads) else ""
        media_ids_array = media_ids_arrays[i] if i < len(media_ids_arrays) else None
        # Add thread counter at the end of each thread
        if No_of_threads == 1:
            thread_counter = f"{thread}\n"
        else:
            thread_counter = f"{thread}\n\n{i+1}/{No_of_threads}"

        if i == 0:
        # Post the first array as a thread
            tweet = client.create_tweet(text=thread_counter, media_ids=media_ids_array)
            tweet_id = tweet.data['id']
            print(f"Thread {i + 1} posted")
        else:
            # Post subsequent arrays as replies
            tweet = client.create_tweet(text=thread_counter, media_ids=media_ids_array, in_reply_to_tweet_id=tweet_id)
            print(f"Thread {i + 1} posted as a reply")

        tweet_id = tweet.data['id']

    print("All threads and replies posted")


def find_media(url, message_id):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response_primary = requests.get(url=f"{telegram_url}/{message_id}?embed=1&mode=tme")
    soup_primary = BeautifulSoup(response_primary.content, "html.parser")
    

    #------------------------- SAVE CAPTION -------------------------#
    if bool(soup_primary.find('div', class_='tgme_widget_message_text')) == True:
        message_div = soup_primary.find('div', class_='tgme_widget_message_text')
        caption = message_div.get_text(strip=True, separator='\n').replace('<br>', '.')
        if contains_rm_word(caption, rm_words):
            return message_id

    if soup_primary.find('div', class_='tgme_widget_message_grouped_wrap'):
        photo_wrap_classes = soup_primary.find_all('a', class_='tgme_widget_message_photo_wrap')
        print(f"Grouped media with {len(photo_wrap_classes)} images")

        for i in range(0, len(photo_wrap_classes)):
            download_url = f"https://t.me/{channel_name}/{message_id+i}?embed=1&mode=tme&single=1"
            
            media_id = download_image(channel_name=channel_name, url=download_url, message_id=message_id+i, api=api)
            media_ids.append(media_id)

    elif soup_primary.find('a', class_='tgme_widget_message_photo_wrap') and not soup_primary.find('div', class_='tgme_widget_message_grouped_wrap'):
        download_url = f"https://t.me/{channel_name}/{message_id}?embed=1&mode=tme"

        media_id = download_image(channel_name=channel_name, url=download_url, message_id=message_id, api=api)
        media_ids.append(media_id)

    media_ids_arrays = [media_ids[i:i + 4] for i in range(0, len(media_ids), 4)]

    formatted_threads = format_caption(caption)
    post_to_twitter(threads=formatted_threads, media_ids_arrays=media_ids_arrays)
    


def download_image(channel_name, url, message_id, api):
    response_sec = requests.get(url)
    soup_sec = BeautifulSoup(response_sec.text, "html.parser")

    if soup_sec.find('div', class_="tgme_widget_message_error"):
        print(f"No media for message_id {message_id}")
        return None

    image_tag = soup_sec.find('a', class_='tgme_widget_message_photo_wrap')
    image_url = image_tag['style'].split('url(')[1].split(')')[0].strip("'")
    filename = f'{message_id}.jpg'

    response = requests.get(image_url)
    with open(filename, 'wb') as img_file:
        img_file.write(response.content)

    # Upload to Twitter
    media_id = api.media_upload(filename=filename).media_id_string

    # Delete local image file
    try:
        os.remove(filename)
    except OSError as e:
        print(f"Error deleting file {filename}: {e}")

    return media_id


find_media(url=telegram_url, message_id=22082)