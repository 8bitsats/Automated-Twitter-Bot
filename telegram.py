import requests
import re
from bs4 import BeautifulSoup

telegram_url = "https://t.me/Nature/20609?embed=1&mode=tme"
response = requests.get(url=telegram_url)
soup = BeautifulSoup(response.content, "html.parser")
channel = telegram_url.split("/")[3]
message_id = telegram_url.split("/")[4].split("?")[0]

def download_video(url):

    # Search for the video tag and extract the 'src' attribute
    video_url = soup.find('video')['src']
    # Download the video
    video_response = requests.get(video_url, stream=True)
    video_response.raise_for_status()

    # Save the video to a local file
    with open(f'{channel}-{message_id}.mp4', 'wb') as file:
        for chunk in video_response.iter_content(chunk_size=8192):
            file.write(chunk)

def download_image(url):

    # Find the anchor tag with the class "tgme_widget_message_photo_wrap" and extract the background-image URL from its style attribute
    image_tag = soup.find('a', class_='tgme_widget_message_photo_wrap')
    image_url = image_tag['style'].split('url(')[1].split(')')[0].strip("'")

    img_response = requests.get(image_url, stream=True)
    img_response.raise_for_status()

    # Save the video to a local file
    with open(f"{channel}-{message_id}.jpg", 'wb') as file:
        for chunk in img_response.iter_content(chunk_size=8192):
            file.write(chunk)

def get_caption(url):

    # Find the div with the class "tgme_widget_message_text" 
    message_div = soup.find('div', class_='tgme_widget_message_text')
    caption = list(message_div.stripped_strings)[0]  # This splits the content based on the presence of tags
    if not caption:
        caption = "#Nature is just amazing 🌎"

    return caption

def post_not_found(url):
    error = soup.find('div', class_="tgme_widget_message_error")
    
    if error and error.text == "Post not found":
        # print("Page not found")
        return True
    else:
        return False

