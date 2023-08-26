import os
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

def initialize_log_file():
    if not os.path.exists('log_file.txt'):
        with open('log_file.txt', 'w') as f:
            f.write("Time, channel, Post ID, Media Type, File Size, Downloaded Time, Caption\n")

def log_to_file(log_values):
    with open('log_file.txt', 'a') as f:
        f.write(', '.join(log_values) + '\n')

def download_video(url):

    # Search for the video tag and extract the 'src' attribute
    video_url = soup.find('video')['src']
    # Download the video
    video_response = requests.get(video_url, stream=True)
    video_response.raise_for_status()

    # Save the video to a local file
    file_size = 0

    with open(f'{channel}-{message_id}.mp4', 'wb') as file:
        for chunk in video_response.iter_content(chunk_size=8192):
            file.write(chunk)
            file_size += len(chunk)
    file_size = file_size / (1024 * 1024)
    log_values.extend([f"{file_size:.2f} MB", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    return True

def download_image(url):

    # Find the anchor tag with the class "tgme_widget_message_photo_wrap" and extract the background-image URL from its style attribute
    image_tag = soup.find('a', class_='tgme_widget_message_photo_wrap')
    image_url = image_tag['style'].split('url(')[1].split(')')[0].strip("'")

    img_response = requests.get(image_url, stream=True)
    img_response.raise_for_status()

    # Save the video to a local file
    file_size = 0

    with open(f"{channel}-{message_id}.jpg", 'wb') as file:
        for chunk in img_response.iter_content(chunk_size=8192):
            file.write(chunk)
            file_size += len(chunk)
    file_size = file_size / (1024 * 1024)
    log_values.extend([f"{file_size:.2f} MB", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    return True

def get_caption(url):

    # Find the div with the class "tgme_widget_message_text" 
    if bool(soup.find('div', class_='tgme_widget_message_text')) == True:
        message_div = soup.find('div', class_='tgme_widget_message_text')
        caption = list(message_div.stripped_strings)[0]  # This splits the content based on the presence of tags
    else:
        caption = "#Nature is just amazing 🌎"
    
    log_values.append(caption)
    return caption


def post_not_found(url):
    error = soup.find('div', class_="tgme_widget_message_error")
    
    if error and error.text == "Post not found":
        # print("Page not found")
        return True
    else:
        return False

initialize_log_file()
for message_id in range(18,30):
    log_values = []
    telegram_url = f"https://t.me/Nature/{message_id}?embed=1&mode=tme"
    response = requests.get(url=telegram_url)
    soup = BeautifulSoup(response.content, "html.parser")
    channel = telegram_url.split("/")[3]

    # validate the link has media
    if post_not_found(telegram_url):
        pass
    else:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_values.extend([current_time, channel, str(message_id)])
        if bool(soup.find('video')) == True:
            log_values.append('Video')
            try:
                download_video(telegram_url)
                # print("video downloaded")
            except TypeError:
                print("No video")
        elif bool(soup.find('a', class_='tgme_widget_message_photo_wrap')) == True:
            log_values.append("Image")
            try:
                download_image(telegram_url)
                # print("image downloaded")
            except None:
                print(f"No image found at url No: {message_id}")
        else:
            continue

        get_caption(telegram_url)
     # Log all values to the log file
    log_to_file(log_values)
        

