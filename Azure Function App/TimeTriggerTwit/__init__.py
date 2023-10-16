from datetime import datetime, timezone
import logging
import random
import re
from io import BytesIO
import azure.functions as func
import requests
from bs4 import BeautifulSoup

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import PublicAccess
from azure.storage.blob import BlobType
import tweepy
from dotenv import load_dotenv
load_dotenv()


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(
        tzinfo=timezone.utc).isoformat()
    
    #********************************Autentication**********************#
    
    # Authenticate Azure
    connection_string = "Your Connection String"
    container_name = "Container Name"
    blob_name = "Blob name" #Log file name. (.txt)

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Check if the container exists, and create it if it doesn't
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()
        container_client.set_container_access_policy(public_access=PublicAccess.Container)

    # Get a reference to the block blob
    media_blob_client = None
    blob_client = blob_service_client.get_blob_client(container_name, blob_name)

    # Check if the blob exists, and create it if it doesn't
    if not blob_client.exists():
        column_titles = "Time, Channel, Message_id, media_type, Tweet_ID"
        blob_client.upload_blob(column_titles, blob_type=BlobType.BlockBlob)

    # authenticate twitter
    try:
        consumer_key = ""
        consumer_secret = ""
        access_token = ""
        access_token_secret = ""
        bearer_token = ""


        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        # Check if Twitter authentication is successful
        user = api.verify_credentials()
        logging.info(f"Twitter authentication successful. User: {user.screen_name}")
        
        # V2 Twitter API Authentication
        client = tweepy.Client(
            bearer_token,
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
            wait_on_rate_limit=True,
        )

    except tweepy.TweepyException as e:
        logging.error(f"Twitter authentication failed: {e}")
        return None
    
    #****************************************************************************************
    
    log_values = []
    channel_name = "CMK_Wallpapers"
    message_id = random.choice(range(0,6500))
    account_name = re.search("AccountName=(.*?);", connection_string).group(1)
    telegram_download_url = f"https://t.me/{channel_name}/{message_id}?embed=1&mode=tme"
    response = requests.get(url=telegram_download_url)
    soup = BeautifulSoup(response.content, "html.parser")
    error = soup.find('div', class_="tgme_widget_message_error")

# --------------------------------------------------------------------------------------------------------#
    # Validate media has not been posted

    # Read the existing data from the blob
    existing_data = blob_client.download_blob().readall() if blob_client.exists() else b""
    
    # Convert the existing data to a string and split it into lines
    existing_lines = existing_data.decode('utf-8').strip().split('\n')
    # numbers = [sublist[2] for sublist in [string.split(',') for string in existing_lines]][1:]
    # numbers = [int(x) for x in numbers]

    numbers = []

    # Skip the first line (assuming it contains column names)
    for string in existing_lines[1:]:
        parts = string.split(',')
        if len(parts) >= 3:
            numbers.append(int(parts[2]))
    
    # Check if the generated number exists in the existing data
    if message_id in numbers:
        logging.warning(f"Number {message_id} already exists in the blob. Skipping.")
        return
    
    # validate the link has media
    if error and error.text == "Post not found":
        pass

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_values.extend([current_time, channel_name, message_id])
    # if bool(soup.find('video')) == True:
    #     log_values.append('Video')
    #     try:
    #         download.download_video(telegram_download_url,channel_name, message_id, log_values)
    #         # print("video downloaded")
    #     except TypeError:
    #         print("No video")
    filename = ''
    if bool(soup.find('a', class_='tgme_widget_message_photo_wrap')) == True:
        log_values.append("Image")

        image_tag = soup.find('a', class_='tgme_widget_message_photo_wrap')
        image_url = image_tag['style'].split('url(')[1].split(')')[0].strip("'")

        img_response = requests.get(image_url, stream=True)
        # img_response.raise_for_status()

        # Create a BlobClient for the file in the container
        filename = f'{channel_name}-{message_id}.jpg'
        media_blob_client = blob_service_client.get_blob_client(container_name, filename)

        # Upload the file's content to Azure Blob Storage
        if not media_blob_client.exists():
            media_blob_client.upload_blob(img_response.content)
            logging.info(f"image {filename} downloaded")
                

# -----------------------------READ THE IMAGE ------------------------------------#

    post_media_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{filename}"
    media_content = requests.get(post_media_url).content

    # Upload the image
    media_file = BytesIO(media_content)

    # Upload image to Twitter.
    media_id = api.media_upload(filename=filename, file=media_file).media_id_string
    log_values.append(media_id)
    logging.info(f"Media ID: {media_id}")

    text = "Hello world!" # Text to be Tweeted
    # Send Tweet with Text and media ID
    client.create_tweet(text=text, media_ids=[media_id])
    logging.info("Tweeted!")


# -------------------------------DELLETE BLOB FILE ------------------------------#

    media_blob_client.delete_blob(delete_snapshots='include')
    logging.info("blob deleted successfully")


# ---------------------------------Append Data-----------------------------------#
    log_values = [str(value) for value in log_values]
    # Append the new data to the blob with a comma separator and a newline character
    updated_data = existing_data + (b'\n' if existing_data else b"") + ','.join(log_values).encode('utf-8')
    
    # Upload the updated data to the blob
    blob_client.upload_blob(updated_data, blob_type=BlobType.BlockBlob, overwrite=True)
        
    if mytimer.past_due:
        logging.info('The timer is past due!')

