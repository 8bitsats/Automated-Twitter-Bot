import re
import tweepy
import random
import logging
import requests
from io import BytesIO
from bs4 import BeautifulSoup
import azure.functions as func
from dotenv import load_dotenv
from datetime import datetime, timezone


load_dotenv()

def authenticate_twitter():
    try:
        consumer_key = os.getenv('API_KEY')
        consumer_secret = os.getenv('API_KEY_SECRET')
        access_token = os.getenv('ACCESS_TOKEN')
        access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
        bearer_token = os.getenv('BEARER_TOKEN')

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


def contains_rm_word(text, rm_words):
    text_lower = text.lower()  # Convert the text to lowercase for case-insensitive matching
    return any(word.lower() in text_lower for word in rm_words)


def format_caption(caption):
    char_count = len(caption)
    num_threads = -(-char_count // 270)
    threads = []
    truncated_word = ""

    # Process each thread
    for i in range(num_threads):
        # Extract the current thread
        thread = caption[i * 270: (i + 1) * 270]

        # Append truncated word from the previous thread
        thread = truncated_word + thread

        # Check if the last character of the thread is part of a word
        if thread[-1].isalnum() and i < num_threads - 1:
            # Find the word that has been truncated and Remove the truncated word from the current thread
            truncated_word = thread.rsplit(' ', 1)[-1]
            thread = thread.rsplit(' ', 1)[0]

        else:
            truncated_word = ""  # Reset truncated word if no word is truncated
        threads.append(thread)

    return threads


def post_to_twitter(threads, media_ids_arrays, client):
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
            thread_counter = f"{thread}\n\n{i + 1}/{No_of_threads}"

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


def find_media(url, message_id, soup_primary, rm_words, channel_name, api):
    error = soup_primary.find('div', class_="tgme_widget_message_error")

    # validate the link has media
    if error and error.text == "Post not found":
        print(f"No post found in in id: {message_id} !!")
        return message_id

    # ------------------------- SAVE CAPTION -------------------------#
    if bool(soup_primary.find('div', class_='tgme_widget_message_text')) == True:
        message_div = soup_primary.find('div', class_='tgme_widget_message_text')
        caption = message_div.get_text(strip=True, separator='\n').replace('<br>', '.')
        if contains_rm_word(caption, rm_words):
            return message_id

    media_ids = []

    if soup_primary.find('div', class_='tgme_widget_message_grouped_wrap'):
        photo_wrap_classes = soup_primary.find_all('a', class_='tgme_widget_message_photo_wrap')
        print(f"Grouped media with {len(photo_wrap_classes)} images")

        with ThreadPoolExecutor() as executor:
            media_ids = list(executor.map(
                lambda i: download_image(channel_name=channel_name, url=f"https://t.me/{channel_name}/{message_id + i}?embed=1&mode=tme&single=1",
                                            message_id=message_id + i, api=api),
                range(len(photo_wrap_classes))
            ))

        # update the new message id
        message_id = message_id + (len(photo_wrap_classes) - 1)

    elif soup_primary.find('a', class_='tgme_widget_message_photo_wrap') and not soup_primary.find(
            'div', class_='tgme_widget_message_grouped_wrap'):
        media_ids.append(download_image(channel_name=channel_name, url=f"https://t.me/{channel_name}/{message_id}?embed=1&mode=tme",
                                        message_id=message_id, api=api))

    media_ids_arrays = [media_ids[i:i + 4] for i in range(0, len(media_ids), 4)]

    formatted_threads = format_caption(caption)
    post_to_twitter(threads=formatted_threads, media_ids_arrays=media_ids_arrays, client=client)
    return message_id


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


def update_message_id(message_id):
    message_id += 1
    file_path = "text_log.txt"
    with open(file_path, "w") as file:
        file.write(str(message_id))
    print("New Message ID:", message_id)


# ************************************ VARIABLES ****************************************************

media_ids = []
api, client = authenticate_twitter()

# Remove Words from the caption
rm_words = ["Telegram", "Channel", "Subscribe", "$", "Blockchain", "Promo", "https://t.me"]

channel_name = "FT_updates"
url = f"https://t.me/{channel_name}"
message_id = 27

while True:
    count+=1
    telegram_url = f"{url}/{message_id}?embed=1&mode=tme"

    response_primary = requests.get(telegram_url)

    if response_primary.status_code == 200:
        soup_primary = BeautifulSoup(response_primary.content, "html.parser")

        # Check if the URL is available
        if bool(soup_primary.find('div', class_='tgme_widget_message_text')) == True:
            message_id = find_media(url=telegram_url, message_id=message_id, soup_primary=soup_primary,
                                    rm_words=rm_words, channel_name=channel_name, api=api)
            update_message_id(message_id)
            # Break the loop once the URL is available
            break

    time.sleep(5)
    if count == 30:
        exit
