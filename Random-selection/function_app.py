'''.
Honest Historian: (1473,3971))
mysteries of earth (315, 8610)
'''
import time
start_time = time.time()

import re
import tweepy
import random
import logging
import requests
from io import BytesIO
import concurrent.futures
from bs4 import BeautifulSoup
from urllib.request import urlopen
import azure.functions as func
from datetime import datetime, timezone
from azure.storage.blob import BlobType
from azure.storage.blob import PublicAccess
from azure.storage.blob import BlobServiceClient
from concurrent.futures import ThreadPoolExecutor

# Remove Words from the caption
unnecessary_words = ["@", "@Honest_historian"]

# Exit if the caption contains promotional words
promotional_words = ["Telegram", "Channel", "Subscribe", "$", "Blockchain", "#Promo", "https://t.me"]


#***************  remove_words ***************************** #
def remove_words(string):
	for word in unnecessary_words:
		if word in string:
			string = string.replace(word, '')
	return string

#***************  contains_promotional_word ***************************** #
def contains_promotional_word(text, promotional_words):
	text_lower = text.lower()  # Convert the text to lowercase for case-insensitive matching
	return any(word.lower() in text_lower for word in promotional_words)


#***************  format_caption ***************************** #
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


#***************  authenticate_twitter ***************************** #
def authenticate_twitter():
	try:
		consumer_key = "79w6DcX2s9igB1MpJSemH7z5r"
		consumer_secret = "9FwW0ITG15V4ZoDojQB2GHvWLL0qmuCjLK6BEsQmwQo6h8DW5R"
		access_token = "1741702421640773632-SiZ4dlSjSeA8IL46cotprwwa6esudc"
		access_token_secret = "FGAcqnHGyKZeQPPW730gSXJgU6Uf6S319qqezWUDPYY79"
		bearer_token = "AAAAAAAAAAAAAAAAAAAAAPBJsAEAAAAAvc07DvgDf1M5yA8%2BaJm7cuo5JUM%3Dt9KB3rBED5J4IEOxPg9ymvY6ZkWVVXmfNl4EIjvG0weOBCHgAu"


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
		return api, client

	except tweepy.TweepyException as e:
		logging.error(f"Twitter authentication failed: {e}")
		return None


#***************  check_blob_url_exists ***************************** #
def check_blob_url_exists(blob_url):
	try:
		response = requests.head(blob_url)
		# Check if the response status code is in the 2xx range (success)
		return response.status_code // 100 == 2
	except requests.RequestException:
		# Handle request exceptions (e.g., network issues)
		return False


#***************  find_media ***************************** #
def find_media(url, message_id, soup, caption, promotional_words, channel_name,
				api, account_name, blob_service_client, container_name, client, log_values):
	media_ids = []

	if soup.find('div', class_='tgme_widget_message_grouped_wrap'):
		photo_wrap_classes = soup.find_all('a', class_='tgme_widget_message_photo_wrap')
		logging.info(f"Grouped media with {len(photo_wrap_classes)} images")

		with ThreadPoolExecutor() as executor:
			media_ids = list(executor.map(
				lambda i: download_image(url=f"https://t.me/{channel_name}/{message_id + i}?embed=1&mode=tme&single=1",
											message_id=message_id + i, api=api, soup=soup, blob_service_client=blob_service_client, 
											container_name=container_name, account_name=account_name),
				range(len(photo_wrap_classes))
			))
			
		# update the new message id
		message_id = message_id + (len(photo_wrap_classes) - 1)

	elif soup.find('a', class_='tgme_widget_message_photo_wrap') and not soup.find(
			'div', class_='tgme_widget_message_grouped_wrap'):
		media_ids.append(download_image(url=f"https://t.me/{channel_name}/{message_id}?embed=1&mode=tme",
										message_id=message_id, api=api, soup=soup, blob_service_client=blob_service_client, 
										container_name=container_name, account_name=account_name))

	media_ids_arrays = [media_ids[i:i + 4] for i in range(0, len(media_ids), 4)]
	log_values.extend(media_ids)

	formatted_threads = format_caption(caption)
	post_to_twitter(threads=formatted_threads, media_ids_arrays=media_ids_arrays, client=client)
	return message_id


#***************  post_to_twitter ***************************** #
def post_to_twitter(threads, media_ids_arrays, client):
	if len(threads) >= len(media_ids_arrays):
		No_of_threads = len(threads)
	else:
		No_of_threads = len(media_ids_arrays)

	tweet_id = None
	try:
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
				# logging.warning(f"Thread {i + 1} posted")
			else:
				# Post subsequent arrays as replies
				tweet = client.create_tweet(text=thread_counter, media_ids=media_ids_array, in_reply_to_tweet_id=tweet_id)
				# logging.warning(f"Thread {i + 1} posted as a reply")

		tweet_id = tweet.data['id']
		logging.info("All threads and replies posted")
	except tweepy.TweepyException as e:
		logging.error(f"Twitter posting Failed {e}")



#***************  download_image ***************************** #
def download_image(url, message_id, api, soup, blob_service_client, container_name, account_name):
	response_sec = requests.get(url)
	soup_sec = BeautifulSoup(response_sec.text, "html.parser")

	image_tag = soup_sec.find('a', class_='tgme_widget_message_photo_wrap')
	image_url = image_tag['style'].split('url(')[1].split(')')[0].strip("'")

	logging.warning(image_url)
	filename = f'{message_id}.jpg'
	response = requests.get(image_url)
	media_blob_client = blob_service_client.get_blob_client(container_name, filename)

	# Upload the file's content to Azure Blob Storage
	if not media_blob_client.exists():
		media_blob_client.upload_blob(response.content)

	post_media_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{filename}"

	exists = check_blob_url_exists(blob_url=post_media_url)

	if exists:
		media_content = requests.get(post_media_url).content
		media_file = BytesIO(media_content)  # Upload the image

	# 	# Upload image to Twitter.
		media_id = api.media_upload(filename=filename, file=media_file).media_id_string

	# -------------------------------DELETE BLOB FILE ------------------------------#
	try:
		media_blob_client.delete_blob(delete_snapshots='include')
		logging.info(f"Image {filename} deleted successfully")
	except AttributeError as e:
		logging.warning("No Blob to delete")

	return media_id


app = func.FunctionApp()

# Schedule timer to execute after every 3 hrs 20 min
@app.schedule(schedule="0 0 */4 * * *", arg_name="myTimer", run_on_startup=True,
				use_monitor=False)

def timer_trigger(myTimer: func.TimerRequest) -> None:
	if myTimer.past_due:
		logging.warning('The timer is past due!')


	# Authenticate Azure
	connection_string = "DefaultEndpointsProtocol=https;AccountName=tweetposts;AccountKey=qG3+CAzcaeGzNsrmDBz5ZvIFbPz89eEaLnfk7nyimjPIRQLEVzMaxYFTOtL4ywpkIKIaHkoTMC/7+AStRWoS1A==;EndpointSuffix=core.windows.net"
	container_name = "honest_historian"
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
		column_titles = "Time, Channel, Message_id, Tweet_ID"
		blob_client.upload_blob(column_titles, blob_type=BlobType.BlockBlob)



	#************************************ VARIABLES ****************************************************
	log_values = []
	media_id = ''
	channel_name = "Honest_historian"
	message_id = random.choice(range(1473,3971))
	account_name = re.search("AccountName=(.*?);", connection_string).group(1)
	telegram_download_url = f"https://t.me/{channel_name}/{message_id}?embed=1&mode=tme"
	response = requests.get(url=telegram_download_url)
	soup = BeautifulSoup(response.text, "html.parser")
	error = soup.find('div', class_="tgme_widget_message_error")
	current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	filename = ''
	log_values.extend([current_time, channel_name, message_id])

	# --------------------------------------------------------------------------------------------------------#
	# Read the existing data from the blob
	existing_data = blob_client.download_blob().readall() if blob_client.exists() else b""
	existing_lines = existing_data.decode('utf-8').strip().split('\n')

	numbers = []

	# Skip the first line it contains column names
	for string in existing_lines[1:]:
		parts = string.split(',')
		if len(parts) >= 3:
			numbers.append(int(parts[2]))


	# Check if the generated number exists in the existing data
	if message_id in numbers:
		logging.warning(f"Number {message_id} already exists in the blob. Skipping.")
		exit(0)

	# validate the link has media
	if error and error.text == "Post not found":
		log_values.append('0')
		logging.error(f"No post found in in id: {message_id} !!")
		exit(0)


	if response.status_code == 200:
		soup = BeautifulSoup(response.content, "html.parser")

	#--------------------- VALIDATE POST WITH CAPTION-------------------#
	if bool(soup.find('div', class_='tgme_widget_message_text')) == True:
		message_div = soup.find('div', class_='tgme_widget_message_text')
		content = message_div.get_text(strip=True, separator='\n').replace('<br>', '.')

		if contains_promotional_word(content, promotional_words):
			log_values.append('0')
			logging.warning(f'Caption at {message_id} is promotional !!')
			exit(0)
		
		caption=remove_words(content) # Eliminate words from a caption

		threads = format_caption(caption)
		logging.info(threads)

	else:
		caption = ""

	api, client = authenticate_twitter()
	find_media(url=telegram_download_url, message_id=message_id, soup=soup, caption=caption,
							promotional_words=promotional_words, channel_name=channel_name,
							api=api, account_name=account_name, blob_service_client=blob_service_client,
							container_name=container_name, client=client, log_values=log_values)

	# ---------------------------------Append Data-----------------------------------#
	log_values = [str(value) for value in log_values]
	# Append the new data to the blob with a comma separator and a newline character
	updated_data = existing_data + (b'\n' if existing_data else b"") + ','.join(log_values).encode('utf-8')

	# Upload the updated data to the blob
	blob_client.upload_blob(updated_data, blob_type=BlobType.BlockBlob, overwrite=True)
	end_time = time.time()
	total_time = end_time - start_time
	logging.info(f"Time: {str(total_time)}")
