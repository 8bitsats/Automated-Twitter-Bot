'''
This code gets content from https://t.me/mqquotes/

'''

import re
import tweepy
import random
import logging
import requests
from io import BytesIO
from bs4 import BeautifulSoup
import azure.functions as func
from datetime import datetime, timezone
from azure.storage.blob import BlobType
from azure.storage.blob import PublicAccess
from azure.storage.blob import BlobServiceClient

# Remove Words from the caption
rm_words = ['@Quotes_Wallpapers', '@mqquotes', '#Motivation', '#mqquotes', '#mq_quotes', 
			'#mqquotes', '#quotes', '@ImQuotes', '#Quotes', '#Mqquotes', '#thoughts', 
			'#thought', '"', ";"]

def remove_words(string):
    for word in rm_words:
        if word in string:
            string = string.replace(word, '')
    return string


def check_blob_url_exists(blob_url):
    try:
        response = requests.head(blob_url)
        # Check if the response status code is in the 2xx range (success)
        return response.status_code // 100 == 2
    except requests.RequestException:
        # Handle request exceptions (e.g., network issues)
        return False


app = func.FunctionApp()

# Schedule timer to execute after every 8 hours
@app.schedule(schedule="0 0 */8 * * *", arg_name="myTimer", run_on_startup=True,
				use_monitor=False)

def timer_trigger(myTimer: func.TimerRequest) -> None:
	if myTimer.past_due:
		logging.info('The timer is past due!')

	#********************************Autentication******************************#

	# Authenticate Azure
	connection_string = ""
	container_name = "quotes"
	blob_name = "logfile.txt"

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
		column_titles = "Time, Channel, Message_id, media_type, Caption, Tweet_ID"
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
		logging.info(f"User {user.screen_name} Authenticated !")

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

# --------------------------------------------------------------------------------------------------------#
	# Read the existing data from the blob
	existing_data = blob_client.download_blob().readall() if blob_client.exists() else b""
	existing_lines = existing_data.decode('utf-8').strip().split('\n')
	logging.info(log_values)

	numbers = []

	# Skip the first line it contains column names
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
		log_values.extend(['No Post', 'No caption' '0'])
		logging.error(f"No post found in in id: {message_id} !!")
		exit(1)


	# ----------------------------- DOWNLOAD VIDEO TO BLOB STORAGE ---------------------------#

		# if bool(soup.find('video')) == True:
		#     log_values.append('Video')
		#     # Search for the video tag and extract the 'src' attribute
		#     video_url = soup.find('video')['src']
		#     video_response = requests.get(video_url, stream=True)
		#     video_response.raise_for_status()

		#     # Create a BlobClient for the file in the container
		#     filename = f'{channel}-{message_id}.mp4'
		#     media_blob_client = blob_service_client.get_blob_client(container_name, filename)

		#     # Upload the file's content to Azure Blob Storage
		#     if not media_blob_client.exists():
		#         media_blob_client.upload_blob(video_response.content)


	# ----------------------------- DOWNLOAD IMAGE TO BLOB STORAGE---------------------------#

	if bool(soup.find('a', class_='tgme_widget_message_photo_wrap')) == True:
		log_values.append("Image")

		image_tag = soup.find('a', class_='tgme_widget_message_photo_wrap')
		image_url = image_tag['style'].split('url(')[1].split(')')[0].strip("'")
		img_response = requests.get(image_url, stream=True)

		# Create a BlobClient for the file in the container
		filename = f'{channel_name}-{message_id}.jpg'
		media_blob_client = blob_service_client.get_blob_client(container_name, filename)

		# Upload the file's content to Azure Blob Storage
		if not media_blob_client.exists():
			media_blob_client.upload_blob(img_response.content)
	else:
		log_values.append("No media")

	#--------------------- SAVE CAPTION-------------------#
	if bool(soup.find('div', class_='tgme_widget_message_text')) == True:
		message_div = soup.find('div', class_='tgme_widget_message_text')
		content = message_div.get_text()
		caption=remove_words(content)

		promotional_text = re.findall("https://t.me", caption)

		if promotional_text:
			log_values.extend(["promotional", "0"])
			logging.error("Caption is promotional")
			media_blob_client.delete_blob(delete_snapshots='include')
			logging.info("blob deleted successfully")
			exit(1)

	else:
		# caption = "#Nature is just amazing 🌎"
		caption = ""

	logging.info(caption)
	log_values.append(caption)


# -----------------------------READ THE MEDIA, CAPTION AND POST TO TWITTER ------------------------------------#

	post_media_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{filename}"

	exists = check_blob_url_exists(blob_url=post_media_url)

	if exists:
		media_content = requests.get(post_media_url).content
		media_file = BytesIO(media_content) # Upload the image

		# Upload image to Twitter.
		media_id = api.media_upload(filename=filename, file=media_file).media_id_string
		log_values.append(media_id)

		# Send Tweet with Text and media ID
		client.create_tweet(text=caption, media_ids=[media_id])
		logging.info("Tweeted!")

	else:
		tweet = client.create_tweet(text=caption)
		log_values.append(tweet.data['id'])
		logging.info("Tweeted without media")

# -------------------------------DELLETE BLOB FILE ------------------------------#

	try:
		media_blob_client.delete_blob(delete_snapshots='include')
		logging.info("blob deleted successfully")
	except AttributeError as e:
		logging.info("No Blob to delete")

	# ---------------------------------Append Data-----------------------------------#
	log_values = [str(value) for value in log_values]
	# Append the new data to the blob with a comma separator and a newline character
	updated_data = existing_data + (b'\n' if existing_data else b"") + ','.join(log_values).encode('utf-8')

	# Upload the updated data to the blob
	blob_client.upload_blob(updated_data, blob_type=BlobType.BlockBlob, overwrite=True)
	exit(0)

